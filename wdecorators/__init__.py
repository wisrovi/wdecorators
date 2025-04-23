from .periodic_scheduller import Periodic_task_sched

from .graylog.loggerg import logger, init_logger, log_exceptions, log_execution_time
from .graylog.middleware import LoggingMiddleware

__all__ = [
    "logger",
    "init_logger",
    "log_exceptions",
    "LoggingMiddleware",
    "Periodic_task_sched",
    "log_execution_time",
]
# __all__ is a list of public objects of that module, as interpreted by import *
# __all__ is a convention in Python that indicates which names should be considered "public" and accessible when the module is imported with a wildcard import (from module import *).
# It helps to control the namespace and avoid exposing internal implementation details.
# By defining __all__, you can specify which names should be accessible when the module is imported with a wildcard import.
# This is useful for encapsulating the module's API and preventing name clashes with other modules.
# In this case, the __all__ list includes the logger, init_logger, log_exceptions, LoggingMiddleware, Periodic_task_sched, and log_execution_time objects from the module.
# This means that when the module is imported with a wildcard import, only these names will be accessible.
# This is useful for encapsulating the module's API and preventing name clashes with other modules.
