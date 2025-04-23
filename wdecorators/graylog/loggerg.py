from functools import wraps
import os
import time
from loguru import logger
from .handler import GraylogUdpHandler


def init_logger(
    log_name="python-app",
    graylog_host: str = None,
    graylog_port: int = 12201,
    log_level: str = "INFO",
):
    global logger

    logger.remove()

    # Graylog UDP
    if os.getenv("GRAYLOG_HOST") or graylog_host:
        logger.add(
            GraylogUdpHandler(
                host=os.getenv("GRAYLOG_HOST", "127.0.0.1"),
                port=int(os.getenv("GRAYLOG_PORT", graylog_port)),
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

    # Local stdout
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=log_level,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )

    return logger


# ---- Decorador útil para logging de excepciones ----
def log_exceptions(
    context: dict = {"send_to_graylog": True},
    enable_raise: bool = False,
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            try:
                return func(*args, **kwargs)
            except Exception as e:
                log = logger.bind(**context)
                log.error(f"Exception in {func.__name__}")

                if enable_raise:
                    raise

        return wrapper

    return decorator


def log_execution_time(context: dict = {"send_to_graylog": False}):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start

            logger.bind(**context).info(f"Executed {func.__name__} in {elapsed:.3f}s")
            return result

        return wrapper

    return decorator
