import logging
import os
import sys
from pathlib import Path

from decouple import (
    RepositoryEnv,
    Config,
)

from common.proxy import (
    get_proxies,
    proxies_to_proxy_settings,
)
from config.uploader_config import UploaderConfig

env_file = os.environ.get('ENV_FILE', ".env")
config = Config(RepositoryEnv(env_file))

PROJECT_ROOT_FOLDER = Path(__file__).resolve().parent.parent


def get_storage_path(uploader_name: str) -> str:
    return str(PROJECT_ROOT_FOLDER / 'storage_states' / f'{uploader_name}_browser_storage.json')


# Check Python version
if sys.version_info < (3, 11):
    logging.getLogger("APP").warning(
        f"Python 3.11 or higher is required (current: {sys.version_info})"
    )

VIDEO_UPLOAD_METHOD = 'upload_video'
PHOTO_UPLOAD_METHOD = 'upload_photo'

SUPPORTED_EXTENSIONS = {
    'video': ('.mp4', '.mov', '.avi', '.mkv'),
    'photo': ('.jpg', '.jpeg', '.png', '.bmp'),
}

METHOD_TO_UPLOAD_SETTINGS_BIND = {
    VIDEO_UPLOAD_METHOD: {
        'folder': config('VIDEOS_FOLDER', default='videos'),
        'supported_extensions': SUPPORTED_EXTENSIONS['video'],
    },
    PHOTO_UPLOAD_METHOD: {
        'folder': config('PHOTOS_FOLDER', default='photos'),
        'supported_extensions': SUPPORTED_EXTENSIONS['photo'],
    },
}

HTTP_PROXY = config('HTTP_PROXY', default=None)
HTTPS_PROXY = config('HTTPS_PROXY', default=None)

DEFAULT_PROXIES = {}

if HTTP_PROXY:
    DEFAULT_PROXIES['http'] = HTTP_PROXY
if HTTPS_PROXY:
    DEFAULT_PROXIES['https'] = HTTPS_PROXY

DEFAULT_HTTPX_PROXY = {'http://': HTTP_PROXY} if HTTP_PROXY else {}

UPLOADER_PARAMETERS = {
    'tiktok': UploaderConfig(
        storage_state=config('TIKTOK_UPLOADER_STORAGE_PATH', default=str(get_storage_path('tiktok'))),
        proxy_settings=proxies_to_proxy_settings(
            get_proxies(config, "TIKTOK_UPLOADER_HTTP_PROXY", "TIKTOK_UPLOADER_HTTPS_PROXY")
        ) or DEFAULT_PROXIES,
        headless=False,
        auth_username=config('TIKTOK_UPLOADER_AUTH_USERNAME'),
        auth_password=config('TIKTOK_UPLOADER_AUTH_PASSWORD')
    ),
}
