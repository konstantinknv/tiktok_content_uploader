import asyncio
from datetime import datetime
from pathlib import Path


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
