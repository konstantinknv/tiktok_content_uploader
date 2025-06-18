import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from moviepy import (
    ImageClip,
    concatenate_videoclips,
)

from config import mainconfig


def collect_files(folder: str, extensions: tuple[str, ...]) -> list[str]:
    path = Path(folder)

    if not path.exists():
        return []

    return [str(p.resolve()) for p in path.iterdir() if p.is_file() and p.suffix.lower() in extensions]


def generate_filename(prefix: str, ext: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{ext}"


async def sleep_on_error(seconds=5):
    await asyncio.sleep(seconds)


async def sleep_on_success(seconds=5):
    await asyncio.sleep(seconds)


def create_slideshow(
    image_files: list,
    output_file: str,
    duration_per_image: int = 5,
    fps: int = 24
) -> str:
    if not image_files:
        raise ValueError("No images provided.")

    clips = []
    for path in image_files:
        clip = ImageClip(path, duration=duration_per_image)
        clips.append(clip)

    video = concatenate_videoclips(clips, method="compose")
    video.write_videofile(output_file, fps=fps, codec="libx264", audio=False, ffmpeg_params=["-pix_fmt", "yuv420p"])
    return output_file


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
