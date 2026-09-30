"""Console + rotating-file logging setup."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOGGER_NAME = "job_automation"
_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(log_dir: Path, level: str = "INFO") -> logging.Logger:
    """Configure the package logger. Safe to call more than once."""
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    for handler in list(logger.handlers):
        handler.close()
        logger.removeHandler(handler)

    formatter = logging.Formatter(_FORMAT)
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    logfile = RotatingFileHandler(
        log_dir / "automation.log", maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    logfile.setFormatter(formatter)
    logger.addHandler(console)
    logger.addHandler(logfile)
    return logger
