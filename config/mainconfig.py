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

env_file = os.environ.get('ENV_FILE', ".env")
config = Config(RepositoryEnv(env_file))

PROJECT_ROOT_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def get_storage_path(uploader_name: str) -> str:
    path = Path(
        os.path.realpath(__file__)).parent.parent / 'storage_states' / f'{uploader_name}_browser_storage.json'
    return str(path)


# Check Python version
if sys.version_info < (3, 11):
    logging.getLogger("APP").warning(
        f"Python 3.11 or higher is required (current: {sys.version_info})"
    )

VIDEO_UPLOAD_METHOD = 'upload_video'
PHOTO_UPLOAD_METHOD = 'upload_photo'

METHOD_TO_UPLOAD_SETTINGS_BIND = {
    VIDEO_UPLOAD_METHOD: {
        'folder': config('VIDEOS_FOLDER', default='videos'),
        'supported_extensions': ('.mp4', '.mov', '.avi', '.mkv'),
    },
    PHOTO_UPLOAD_METHOD: {
        'folder': config('PHOTOS_FOLDER', default='photos'),
        'supported_extensions': ('.jpg', '.jpeg', '.png', '.bmp'),
    },
}

HTTP_PROXY = config('HTTP_PROXY', default=None)
HTTPS_PROXY = config('HTTPS_PROXY', default=None)

DEFAULT_PROXIES = {}
DEFAULT_HTTPX_PROXY = {}

if HTTP_PROXY:
    DEFAULT_PROXIES['http'] = HTTP_PROXY
    DEFAULT_HTTPX_PROXY['http://'] = HTTP_PROXY
if HTTPS_PROXY:
    DEFAULT_PROXIES['https'] = HTTPS_PROXY

AUTH_USERNAME_KEY = 'auth_username'
AUTH_PASSWORD_KEY = 'auth_password'

UPLOADER_PARAMETERS = {
    'tiktok': {
        'proxy_settings': proxies_to_proxy_settings(
            get_proxies(config, "TIKTOK_UPLOADER_HTTP_PROXY", "TIKTOK_UPLOADER_HTTPS_PROXY")
        ) or DEFAULT_PROXIES,
        'headless': False,
        'storage_state': config('TIKTOK_UPLOADER_STORAGE_PATH', default=get_storage_path('tiktok')),
        AUTH_USERNAME_KEY: config('TIKTOK_UPLOADER_AUTH_USERNAME'),
        AUTH_PASSWORD_KEY: config('TIKTOK_UPLOADER_AUTH_PASSWORD'),
    },
}
