import os
import random
from asyncio import sleep

from common.exceptions import AuthException
from common.utils import create_slideshow
from common.utils import generate_filename
from config import mainconfig
from uploaders.base.base_uploader import BaseUploader
from . import UPLOADER_NAME


class ContentUploader(BaseUploader):
    DOMAIN_URL = 'https://www.tiktok.com?lang=en'
    PROFILE_URL = 'https://www.tiktok.com/profile?lang=en'
    UPLOAD_PAGE_URL = 'https://www.tiktok.com/tiktokstudio/upload?from=webapp&lang=en'

    def __init__(self):
        self.uploader_parameters = mainconfig.UPLOADER_PARAMETERS[UPLOADER_NAME]
        super().__init__(uploader_name=UPLOADER_NAME, **self.uploader_parameters)

    async def upload_photo(self, files: list, *args, **kwargs) -> None:
        await self._upload_slideshow(files)

    async def upload_video(self, files: list, *args, **kwargs) -> None:
        await self._warm_up_browser()
        await self._login()

        for file in files:
            await self._perform_video_upload(file)

    async def _upload_slideshow(self, files: list) -> None:
        slideshow = await self._generate_slideshow(files)

        try:
            await self._warm_up_browser()
            await self._login()
            await self._perform_video_upload(slideshow)
        except BaseException as e:
            raise e
        finally:
            self._delete_temp_file(file_path=slideshow)

    async def _is_logged_in(self) -> bool:
        if not self.uploader_parameters.get(mainconfig.AUTH_USERNAME_KEY) \
                or not self.uploader_parameters.get(mainconfig.AUTH_PASSWORD_KEY):
            self._logger.warning(f'Username and/or password is not set for uploader: {UPLOADER_NAME}')
            return True

        await self._open_page(url=self.PROFILE_URL)

        try:
            edit_profile_button = self._page.locator(
                selector='//button[@data-e2e="edit-profile-entrance"]',
            )
            await edit_profile_button.wait_for(state="visible", timeout=10_000)
            return True
        except BaseException:
            return False

    async def _login(self) -> None:
        if await self._is_logged_in():
            self._logger.info('Already logged in!')
            return

        await self._open_page(url=self.DOMAIN_URL)
        profile_button = self._page.locator(
            selector='//button[@aria-label="Profile"]',
        )
        await profile_button.wait_for(state="visible", timeout=10_000)
        await profile_button.click()
        show_email_and_passw_auth_button = self._page.locator(
            selector='//div[@id="login-modal"]//div[@data-e2e="channel-item" and .//*[contains(text(), "mail")]]',
        )
        await show_email_and_passw_auth_button.wait_for(state="visible", timeout=10_000)
        await show_email_and_passw_auth_button.click()
        login_with_email_and_password_button = self._page.locator(
            selector='//a[contains(@href, "/login/phone-or-email/email")]',
        )
        await login_with_email_and_password_button.wait_for(state="visible", timeout=10_000)
        await login_with_email_and_password_button.click()
        await self._page.type(
            selector='//input[@name="username"]',
            text=self.uploader_parameters[mainconfig.AUTH_USERNAME_KEY],
            timeout=10_000,
            delay=random.randint(100, 500),
        )
        await self._page.type(
            selector='//input[@type="password"]',
            text=self.uploader_parameters[mainconfig.AUTH_PASSWORD_KEY],
            timeout=random.randint(100, 500),
        )
        submit_button = self._page.locator(
            selector='//button[@type="submit" and @data-e2e="login-button"]',
        )
        await submit_button.wait_for(state="visible", timeout=10_000)
        await submit_button.click()
        await sleep(5)

        if not await self._is_logged_in():
            raise AuthException('Cannot log in!')

        await self._save_storage_state_if_required()
        self._logger.info('Login is successful!')

    async def _perform_video_upload(self, file: str) -> None:
        await self._open_page(self.UPLOAD_PAGE_URL)
        await sleep(3)
        file_input = await self._page.query_selector(
            selector='//input[@type="file"]',
        )
        await file_input.set_input_files(file)
        await self._page.evaluate('''element => {
            const event = new Event('change', { bubbles: true });
            element.dispatchEvent(event);
        }''', file_input)
        post_confirmation_button = self._page.locator(
            selector='//button[@data-e2e="post_video_button"]',
        )
        await post_confirmation_button.wait_for(state="visible", timeout=10_000)
        await post_confirmation_button.click()

    async def _generate_slideshow(self, files: list) -> str:
        slideshow_file_path = self._create_temp_file_path()
        return create_slideshow(
            image_files=files,
            output_file=slideshow_file_path,
        )

    def _create_temp_file_path(self) -> str:
        slideshow_file_name = generate_filename(
            prefix='slideshow',
            ext='mp4',
        )
        return os.path.join(self.path_to_temp_folder, slideshow_file_name)

    def _delete_temp_file(self, file_path: str) -> bool:
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return True
            else:
                self._logger.error(f'Cannot delete file "{file_path}". File not found')
                return False
        except BaseException as e:
            self._logger.error(f'Cannot delete file "{file_path}" due to an error: {e}')
            return False
