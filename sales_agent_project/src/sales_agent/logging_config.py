"""
Logging configuration for the Sales Agent system.

WHY proper logging matters:
- Print statements can't be filtered by severity
- Print statements can't be easily redirected to files
- Print statements don't include timestamps, source location, etc.
- Logging can be configured differently for dev/prod environments

HOW Python logging works:
- Loggers form a hierarchy (sales_agent.tools.email inherits from sales_agent)
- Handlers determine WHERE logs go (console, file, external service)
- Formatters determine HOW logs look
- Levels filter WHAT gets logged (DEBUG, INFO, WARNING, ERROR, CRITICAL)
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,) -> logging.Logger:

    logger = logging.getLogger("sales_agent")
    logger.setLevel(level)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    if name.startswith("sales_agent"):
        return logging.getLogger(name)
    return logging.getLogger(f"sales_agent.{name}")