import os
import sys
from typing import Optional

from config import mainconfig


def find_chrome_executable() -> Optional[str]:
    base_dir = os.path.join(os.getcwd(), os.path.join(mainconfig.PROJECT_ROOT_FOLDER, 'chromium'))

    if sys.platform.startswith('win'):
        target_name = 'chrome.exe'
    else:
        target_name = 'chrome'

    for root, dirs, files in os.walk(base_dir):
        if target_name in files:
            full_path = os.path.join(root, target_name)
            return os.path.abspath(full_path)

    return None
