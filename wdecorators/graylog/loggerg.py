"""Graylog logger initialization and decorators."""

import os
import time
from functools import wraps
from typing import Any, Callable, Dict, Optional

from loguru import logger

from .handler import GraylogUdpHandler


def init_logger(
    log_name: str = "python-app",
    graylog_host: Optional[str] = None,
    graylog_port: int = 12201,
    log_level: str = "INFO",
):
    """Initialize and configure the loguru logger with Graylog and console sinks.

    Args:
        log_name: Application name for log identification.
        graylog_host: Graylog server hostname. Falls back to GRAYLOG_HOST env var.
        graylog_port: Graylog GELF UDP port. Falls back to GRAYLOG_PORT env var.
        log_level: Minimum log level (e.g., 'INFO', 'DEBUG', 'ERROR').

    Returns:
        Configured loguru logger instance.
    """
    logger.remove()

    if os.getenv("GRAYLOG_HOST") or graylog_host:
        logger.add(
            GraylogUdpHandler(
                host=os.getenv("GRAYLOG_HOST", "127.0.0.1"),
                port=int(os.getenv("GRAYLOG_PORT", str(graylog_port))),
                log_name=log_name,
            ),
            level=os.getenv("LOG_LEVEL", log_level),
            format="{message}",
            filter=lambda r: r["extra"].get("send_to_graylog", False),
            backtrace=True,
            diagnose=True,
        )

    if os.getenv("APP_ENV", "dev") == "dev":
        logger.add("logs/dev.log", rotation="1 MB", level="DEBUG")

    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level>"
        " | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>"
        " - <level>{message}</level>",
    )

    return logger


def log_exceptions(
    context: Optional[Dict[str, Any]] = None, enable_raise: bool = False
):
    """Decorator that catches exceptions and logs them via loguru.

    Args:
        context: Extra context to bind to the logger (e.g., send_to_graylog).
        enable_raise: If True, re-raises the exception after logging.

    Returns:
        Decorated function.
    """
    if context is None:
        context = {"send_to_graylog": True}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log = logger.bind(**context)
                log.error(f"Exception in {func.__name__}: {e}")

                if enable_raise:
                    raise

        return wrapper

    return decorator


def log_execution_time(context: Optional[Dict[str, Any]] = None):
    """Decorator that logs the execution time of the decorated function.

    Args:
        context: Extra context to bind to the logger (e.g., send_to_graylog).

    Returns:
        Decorated function.
    """
    if context is None:
        context = {"send_to_graylog": False}

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start

            logger.bind(**context).info(f"Executed {func.__name__} in {elapsed:.3f}s")
            return result

        return wrapper

    return decorator
