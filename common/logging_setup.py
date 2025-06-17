import logging
import sys
from typing import Literal, Optional

try:
    import colorama
    colorama.init()
    COLORAMA_ENABLED = True
except ImportError:
    COLORAMA_ENABLED = False

LOG_LEVEL = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

_formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%H:%M:%S'
)


class ColorFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',
        'INFO': '\033[92m',
        'WARNING': '\033[93m',
        'ERROR': '\033[91m',
        'CRITICAL': '\033[1;91m'
    }
    RESET = '\033[0m'

    def format(self, record):
        msg = super().format(record)
        if COLORAMA_ENABLED:
            color = self.COLORS.get(record.levelname, '')
            return f"{color}{msg}{self.RESET}"
        return msg


def setup_logging(
    level: LOG_LEVEL = 'INFO',
    log_file: Optional[str] = None,
    use_colors: bool = True
):
    if logging.getLogger().hasHandlers():
        logging.getLogger().handlers.clear()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    if use_colors and COLORAMA_ENABLED:
        console_handler.setFormatter(ColorFormatter(_formatter._fmt, _formatter.datefmt))
    else:
        console_handler.setFormatter(_formatter)

    handlers = [console_handler]

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel('DEBUG')
        file_handler.setFormatter(_formatter)
        handlers.append(file_handler)

    logging.basicConfig(level=level, handlers=handlers, force=True)


def get_named_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
