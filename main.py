import argparse
import asyncio

from common.module_loader import load_uploader_module
from common.utils import (
    collect_files,
    sleep_on_error,
    sleep_on_success,
)
from common.logging_setup import (
    setup_logging,
    get_named_logger,
)
from config import mainconfig


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Media uploader CLI")
    parser.add_argument(
        "-r",
        "--uploader",
        required=True,
        help="Uploader name, e.g. 'tiktok'"
    )
    method_choices = [
        mainconfig.VIDEO_UPLOAD_METHOD,
        mainconfig.PHOTO_UPLOAD_METHOD,
    ]
    parser.add_argument(
        "method",
        choices=method_choices,
        help=f"What to upload: accepts [{', '.join(method_choices)}]"
    )
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    setup_logging()
    logger = get_named_logger('main')

    try:
        uploader_class, uploader_name = load_uploader_module(args.uploader)
    except ModuleNotFoundError:
        logger.error(f"Uploader '{args.uploader}' not found.")
        await sleep_on_error()
        return

    uploader = uploader_class()
    logger.info(f"Uploader initialized: {uploader_name}")

    upload_settings = mainconfig.METHOD_TO_UPLOAD_SETTINGS_BIND.get(args.method)

    if not upload_settings:
        logger.error(f"No upload settings found for method '{args.method}'.")
        await sleep_on_error()
        return

    files_folder = upload_settings.get("folder")
    extensions = upload_settings.get("supported_extensions")

    if not files_folder:
        logger.error(f"No folder is bind for method {args.method}.")
        await sleep_on_error()
        return

    files = collect_files(files_folder, extensions)

    if not files:
        logger.error(f"No files found for {args.method}.")
        await sleep_on_error()
        return

    method = getattr(uploader, args.method, None)

    if not callable(method):
        logger.error(f"Method '{args.method}' is not implemented in {uploader_name} uploader.")
        await sleep_on_error()
        return

    try:
        logger.info(f"Starting upload of {len(files)} file(s)...")

        async with uploader:
            try:
                if asyncio.iscoroutinefunction(method):
                    await method(files)
                else:
                    method(files)
            except BaseException as e:
                logger.exception(f"Error during upload: {e}")
                await sleep_on_error()
                return

        logger.info(f"Successfully uploaded {len(files)} file(s)!")
        await sleep_on_success()
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        await sleep_on_error()


if __name__ == '__main__':
    asyncio.run(main())
