API Reference
=============

All decorators are importable directly from the ``wdecorators`` package.

::

    from wdecorators import benchmark, retry, timeout, ...

---

Summary Table
-------------

.. list-table:: Complete decorator reference
   :header-rows: 1
   :widths: 20 30 15 35

   * - Decorator
     - Import
     - Category
     - Description
   * - ``@accepts``
     - ``from wdecorators import accepts``
     - Validation
     - Validate positional argument types
   * - ``@benchmark``
     - ``from wdecorators import benchmark``
     - Performance
     - Measure and log execution time
   * - ``@cached_property``
     - ``from wdecorators import cached_property``
     - Optimization
     - Cached property with invalidation
   * - ``@coerce_types``
     - ``from wdecorators import coerce_types``
     - Validation
     - Coerce kwargs to target types
   * - ``@conditional``
     - ``from wdecorators import conditional``
     - Flow Control
     - Execute only if predicate returns True
   * - ``@context_logger``
     - ``from wdecorators import context_logger``
     - Logging
     - Log function entry/exit with module context
   * - ``@count_calls``
     - ``from wdecorators import count_calls``
     - Debugging
     - Track and report call count
   * - ``@debounce``
     - ``from wdecorators import debounce``
     - Flow Control
     - Debounce rapid function calls
   * - ``@debug_arguments``
     - ``from wdecorators import debug_arguments``
     - Debugging
     - Log all arguments passed to function
   * - ``@default_values``
     - ``from wdecorators import default_values``
     - Utilities
     - Set default values for keyword arguments
   * - ``@deprecated``
     - ``from wdecorators import deprecated``
     - Utilities
     - Mark function as deprecated, emit warning
   * - ``@disk_cache``
     - ``from wdecorators import disk_cache``
     - Caching
     - Persistent on-disk cache (pickle/json)
   * - ``@ensure_kwargs``
     - ``from wdecorators import ensure_kwargs``
     - Utilities
     - Convert positional args to keyword args
   * - ``@ignore_kwargs``
     - ``from wdecorators import ignore_kwargs``
     - Utilities
     - Silently ignore specified kwargs
   * - ``@lazy_property``
     - ``from wdecorators import lazy_property``
     - Optimization
     - Property computed once on first access
   * - ``@log_exceptions``
     - ``from wdecorators import log_exceptions_general``
     - Resilience
     - Catch exceptions, log, return fallback
   * - ``@log_return``
     - ``from wdecorators import log_return``
     - Debugging
     - Log the return value of a function
   * - ``@mask_sensitive``
     - ``from wdecorators import mask_sensitive``
     - Security
     - Mask sensitive argument values in logs
   * - ``@memoize``
     - ``from wdecorators import memoize``
     - Caching
     - In-memory cache keyed by arguments
   * - ``@notify_on_error``
     - ``from wdecorators import notify_on_error``
     - Resilience
     - Execute callback when function raises exception
   * - ``@periodic_execution``
     - ``from wdecorators import periodic_execution``
     - Utilities
     - Run function periodically in background thread
   * - ``@profile_memory``
     - ``from wdecorators import profile_memory``
     - Performance
     - Trace memory usage with tracemalloc
   * - ``@rate_limit``
     - ``from wdecorators import rate_limit``
     - Resilience
     - Limit calls per second (delays excess)
   * - ``@repeat``
     - ``from wdecorators import repeat``
     - Flow Control
     - Execute function N times, collect results
   * - ``@require_authentication``
     - ``from wdecorators import require_authentication``
     - Security
     - Check user is authenticated before execution
   * - ``@retry``
     - ``from wdecorators import retry``
     - Resilience
     - Retry on any exception up to N times
   * - ``@retry_on_exception``
     - ``from wdecorators import retry_on_exception``
     - Resilience
     - Retry with delay on specific exceptions
   * - ``@returns``
     - ``from wdecorators import returns``
     - Validation
     - Validate function return type
   * - ``@run_once``
     - ``from wdecorators import run_once``
     - Flow Control
     - Execute function only once, cache result
   * - ``@sanitize_input``
     - ``from wdecorators import sanitize_input``
     - Security
     - HTML-escape all string arguments
   * - ``@silent_fail``
     - ``from wdecorators import silent_fail``
     - Resilience
     - Silence all exceptions, return None
   * - ``@singleton``
     - ``from wdecorators import singleton``
     - Utilities
     - Ensure only one class instance
   * - ``@suppress``
     - ``from wdecorators import suppress``
     - Resilience
     - Suppress specific exceptions with fallback
   * - ``@synchronized``
     - ``from wdecorators import synchronized``
     - Concurrency
     - Thread-safe execution with a lock
   * - ``@throttle``
     - ``from wdecorators import throttle``
     - Resilience
     - Limit calls per interval (drops excess)
   * - ``@time_execution``
     - ``from wdecorators import time_execution``
     - Performance
     - Measure and log execution duration
   * - ``@timeout``
     - ``from wdecorators import timeout``
     - Resilience
     - Raise TimeoutException if exceeded
   * - ``@to_json``
     - ``from wdecorators import to_json``
     - Utilities
     - Convert return value to JSON string
   * - ``@trace_execution``
     - ``from wdecorators import trace_execution``
     - Debugging
     - Log function entry and exit
   * - ``@transform``
     - ``from wdecorators import transform``
     - Utilities
     - Transform return value through a function
   * - ``@ttl_cache``
     - ``from wdecorators import ttl_cache``
     - Caching
     - Time-to-live cache with LRU eviction
   * - ``@validate_length``
     - ``from wdecorators import validate_length``
     - Validation
     - Validate string/list argument length
   * - ``@validate_range``
     - ``from wdecorators import validate_range``
     - Validation
     - Validate numeric argument range
   * - ``@validate_types``
     - ``from wdecorators import validate_types``
     - Validation
     - Runtime type checking for keyword arguments
   * - ``@wait_until``
     - ``from wdecorators import wait_until``
     - Flow Control
     - Wait for predicate before executing
   * - ``init_logger``
     - ``from wdecorators import init_logger``
     - Graylog
     - Configure loguru with Graylog UDP + console
   * - ``log_exceptions``
     - ``from wdecorators import log_exceptions``
     - Graylog
     - Log exceptions to Graylog
   * - ``log_execution_time``
     - ``from wdecorators import log_execution_time``
     - Graylog
     - Log execution time to Graylog
   * - ``Periodic_task_sched``
     - ``from wdecorators import Periodic_task_sched``
     - Scheduler
     - Periodic task scheduler with FastAPI dashboard

---

Performance
-----------

.. automodule:: wdecorators.general.benchmark
   :members:

.. automodule:: wdecorators.general.time_execution
   :members:

.. automodule:: wdecorators.general.profile_memory
   :members:

.. automodule:: wdecorators.general.memoize
   :members:

.. automodule:: wdecorators.general.disk_cache
   :members:

.. automodule:: wdecorators.general.ttl_cache
   :members:

Resilience
----------

.. automodule:: wdecorators.general.retry
   :members:

.. automodule:: wdecorators.general.retry_on_exception
   :members:

.. automodule:: wdecorators.general.timeout
   :members:

.. automodule:: wdecorators.general.rate_limit
   :members:

.. automodule:: wdecorators.general.throttle
   :members:

.. automodule:: wdecorators.general.silent_fail
   :members:

.. automodule:: wdecorators.general.suppress
   :members:

.. automodule:: wdecorators.general.log_exceptions
   :members:

.. automodule:: wdecorators.general.notify_on_error
   :members:

.. automodule:: wdecorators.general.synchronized
   :members:

Debugging
---------

.. automodule:: wdecorators.general.debug_arguments
   :members:

.. automodule:: wdecorators.general.trace_execution
   :members:

.. automodule:: wdecorators.general.log_return
   :members:

.. automodule:: wdecorators.general.count_calls
   :members:

.. automodule:: wdecorators.general.context_logger
   :members:

Validation
----------

.. automodule:: wdecorators.general.validate_types
   :members:

.. automodule:: wdecorators.general.validate_range
   :members:

.. automodule:: wdecorators.general.validate_length
   :members:

.. automodule:: wdecorators.general.accepts
   :members:

.. automodule:: wdecorators.general.returns
   :members:

.. automodule:: wdecorators.general.coerce_types
   :members:

Security
--------

.. automodule:: wdecorators.general.sanitize_input
   :members:

.. automodule:: wdecorators.general.mask_sensitive
   :members:

.. automodule:: wdecorators.general.require_authentication
   :members:

Utilities & Flow Control
------------------------

.. automodule:: wdecorators.general.singleton
   :members:

.. automodule:: wdecorators.general.to_json
   :members:

.. automodule:: wdecorators.general.periodic_execution
   :members:

.. automodule:: wdecorators.general.deprecated
   :members:

.. automodule:: wdecorators.general.conditional
   :members:

.. automodule:: wdecorators.general.repeat
   :members:

.. automodule:: wdecorators.general.run_once
   :members:

.. automodule:: wdecorators.general.debounce
   :members:

.. automodule:: wdecorators.general.wait_until
   :members:

.. automodule:: wdecorators.general.transform
   :members:

.. automodule:: wdecorators.general.default_values
   :members:

.. automodule:: wdecorators.general.ignore_kwargs
   :members:

.. automodule:: wdecorators.general.ensure_kwargs
   :members:

.. automodule:: wdecorators.general.cached_property
   :members:

.. automodule:: wdecorators.general.lazy_property
   :members:

Graylog Integration
-------------------

.. automodule:: wdecorators.graylog.loggerg
   :members:

.. automodule:: wdecorators.graylog.middleware
   :members:

Periodic Task Scheduler
-----------------------

.. autoclass:: wdecorators.periodic_scheduller.controller.Periodic_task_sched
   :members:
