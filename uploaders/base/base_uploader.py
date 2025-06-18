import os
import subprocess
import sys
from abc import (
    ABC,
    abstractmethod,
)
from pathlib import Path
from typing import (
    AsyncContextManager,
    Optional,
    Any,
)

from playwright.async_api import (
    async_playwright,
    ProxySettings,
    Page,
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
)

from common.utils import find_chrome_executable
from common.logging_setup import get_named_logger
from config.mainconfig import PROJECT_ROOT_FOLDER

_BROWSER_ARGS = []
_HEADLESS_BROWSER_ARGS = [
    "--disable-gpu",
    "--disable-web-security",
    "--disable-xss-auditor",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--allow-running-insecure-content",
    "--disable-webgl",
    "--disable-popup-blocking",
    "--disable-dev-shm-usage",
    "--disable-blink-features=AutomationControlled",
]


class BaseUploader(AsyncContextManager, ABC):
    WARMUP_URLS = [
        "https://www.google.com",
        "https://www.wikipedia.org",
        "https://www.youtube.com"
    ]

    def __init__(self, *, uploader_name: str, proxy_settings: ProxySettings = None, headless: bool = True,
                 storage_state: str = None, save_storage_state_on_exit: bool = True, **kwargs):
        self._logger = get_named_logger(uploader_name)
        self._uploader_name = uploader_name
        self._proxy_settings = proxy_settings
        self._headless = headless
        self._storage_state = storage_state
        self._save_storage_state_on_exit = save_storage_state_on_exit

    async def __aenter__(self) -> "BaseUploader":
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            executable_path=self._download_chrome_with_h264_codec(),
            headless=self._headless,
            args=_BROWSER_ARGS if not self._headless else _HEADLESS_BROWSER_ARGS,
            proxy={
                'server': 'http://per-context'
            } if self._proxy_settings else None,
        )
        new_page_kwargs = {}

        if self._storage_state and os.path.exists(self._storage_state):
            self._logger.info('Creating page using the storage state')
            new_page_kwargs['storage_state'] = self._storage_state
        else:
            self._logger.info('Creating page without the storage state')

        self._page = await self._browser.new_page(
            viewport={"width": 1440, "height": 768},
            proxy=self._proxy_settings if self._proxy_settings else None,
            **new_page_kwargs
        )
        await self._patch_navigator_webdriver()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> Optional[bool]:
        storage_state_saved = await self._save_storage_state_if_required()
        browser_closed = await self._close_browser()
        return storage_state_saved and browser_closed

    def _download_chrome_with_h264_codec(self) -> str:
        executable_path = find_chrome_executable()

        if executable_path:
            return executable_path

        self._logger.info("Chromium not found, executing download script...")

        project_root = os.path.abspath(PROJECT_ROOT_FOLDER)

        if sys.platform.startswith('win'):
            script_path = os.path.join(project_root, 'download_chromium.bat')
            subprocess.run([script_path], check=True, timeout=1200)
        elif sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            script_path = os.path.join(project_root, 'download_chromium.bash')
            subprocess.run(['bash', script_path], check=True, timeout=1200)
        else:
            raise RuntimeError("Unsupported platform")

        self._logger.info("Chromium download and extraction completed successfully.")

        executable_path = find_chrome_executable()

        if not executable_path:
            self._logger.error("Chromium executable not found after script execution.")
            raise FileNotFoundError("Chromium executable not found after running the download script.")

        return executable_path

    async def _save_storage_state_if_required(self) -> bool:
        try:
            if self._save_storage_state_on_exit and self._page and self._storage_state:
                await self._page.context.storage_state(path=self._storage_state)
                self._logger.info(f"[{self._uploader_name}] Storage state updated")
                return True
        except Exception as e:
            self._logger.error(f"[{self._uploader_name}] Failed to save storage state: {e}")
            return False

    async def _close_browser(self) -> bool:
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()

            return True
        except Exception as e:
            self._logger.warning(f"[{self._uploader_name}] Error occurred while stopping playwright: {e}")
            return False

    async def _patch_navigator_webdriver(self) -> None:
        patch_script = """
        if (navigator.webdriver === false) {
            // Post Chrome 89.0.4339.0 and already good
        } else if (navigator.webdriver === undefined) {
            // Pre Chrome 89.0.4339.0 and already good
        } else {
            // Pre Chrome 88.0.4291.0 and needs patching
            delete Object.getPrototypeOf(navigator).webdriver
        }
        """
        await self._page.add_init_script(patch_script)

    async def _warm_up_browser(self) -> None:
        self._logger.info(f"[{self._uploader_name}] Starting browser warm-up sequence...")

        for url in self.WARMUP_URLS:
            try:
                self._logger.debug(f"[{self._uploader_name}] Warming up with: {url}")
                response = await self._page.goto(url, wait_until="domcontentloaded", timeout=10000)

                if response and response.ok:
                    self._logger.debug(f"[{self._uploader_name}] Warm-up page loaded successfully: {url}")
                else:
                    self._logger.warning(f"[{self._uploader_name}] Failed warm-up load: {url}")

                await self._page.wait_for_timeout(1500)
            except Exception as e:
                self._logger.warning(f"[{self._uploader_name}] Error during warm-up on {url}: {e}")

        self._logger.info(f"[{self._uploader_name}] Browser warm-up complete.")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(BaseException),
        reraise=True
    )
    async def _open_page(self, url: str, timeout: int = 30000) -> Page:
        self._logger.info(f"[{self._uploader_name}] Trying to open page: {url}")

        response = await self._page.goto(url, timeout=timeout, wait_until="domcontentloaded")

        if not response or not response.ok:
            raise Exception(f"Failed to load page or bad response: {response.status if response else 'No response'}")

        self._logger.info(f"[{self._uploader_name}] Successfully opened: {url}")
        return self._page

    @property
    def path_to_temp_folder(self):
        project_root = Path(__file__).parent.parent.parent
        temp_folder = project_root / 'temp'
        temp_folder_full_path = temp_folder.resolve()
        return temp_folder_full_path

    @abstractmethod
    async def upload_video(self, files: list, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def upload_photo(self, files: list, *args, **kwargs) -> Any:
        pass
