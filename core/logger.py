"""
logger module
provides centralized logging configuration for connect 4.
directs output to a file to avoid interfering with the rich terminal ui.
"""

import logging
from pathlib import Path


def setup_logging(
    log_file: str = "logs/game.log", level: int = logging.INFO
) -> None:
    """
    configures root logger to write timestamped logs to a designated file.

    :param log_file: relative or absolute path to log output file
    :param level: logging sensitivity level (default INFO)
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    file_handler = logging.FileHandler(log_path, mode="a", encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # avoid duplicate handlers if setup_logging is called multiple times
    if not any(isinstance(h, logging.FileHandler) for h in root_logger.handlers):
        root_logger.addHandler(file_handler)


# alias for convenience
setup_log = setup_logging
