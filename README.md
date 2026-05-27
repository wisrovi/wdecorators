# wdecorators

[![PyPI version](https://img.shields.io/pypi/v/wdecorators.svg)](https://pypi.org/project/wdecorators/)
[![Python Versions](https://img.shields.io/pypi/pyversions/wdecorators.svg)](https://pypi.org/project/wdecorators/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**wdecorators** is a high-level Python decorator library providing a collection of ready-to-use decorators for performance profiling, resilience (retry, timeout, rate-limiting), debugging, input sanitization, structured logging with Graylog, caching, and periodic task scheduling.

---

## Installation

```bash
pip install wdecorators
```

### Optional extras

```bash
# For the periodic task scheduler dashboard (FastAPI + Uvicorn + JWT)
pip install wdecorators[scheduler]

# For the Graylog FastAPI middleware
pip install wdecorators[graylog]
```

---

## Quick Start

```python
from wdecorators import benchmark, retry, time_execution, singleton

@benchmark
def my_function():
    return sum(range(1000))

@retry(times=3)
def unreliable_function():
    import random
    if random.random() < 0.5:
        raise ConnectionError("Network issue")
    return "OK"

@singleton
class Database:
    def __init__(self):
        print("Connecting to database...")

print(my_function())
print(unreliable_function())
db1 = Database()
db2 = Database()
print(db1 is db2)  # True
```

---

## Decorator Reference

### Performance

| Decorator | Description |
|-----------|-------------|
| `@benchmark` | Measures and prints function execution time |
| `@time_execution` | Same as benchmark (alias) |
| `@profile_memory` | Traces memory usage with `tracemalloc` |
| `@memoize` | In-memory cache keyed by arguments |
| `@disk_cache(filename)` | Persistent pickle-based cache on disk |

### Resilience

| Decorator | Description |
|-----------|-------------|
| `@retry(times)` | Retries on any exception up to `times` attempts |
| `@retry_on_exception(retries, delay, exceptions)` | Retries on specific exception types with delay |
| `@timeout(seconds)` | Raises `TimeoutException` if execution exceeds limit |
| `@rate_limit(calls_per_second)` | Limits invocation rate |
| `@silent_fail` | Silences exceptions and returns `None` |
| `@log_exceptions` | Catches exceptions and logs error message |

### Debugging

| Decorator | Description |
|-----------|-------------|
| `@debug_arguments` | Prints function arguments on each call |
| `@trace_execution` | Prints entry/exit trace messages |
| `@log_return` | Prints the return value |
| `@count_calls` | Tracks and prints call count |
| `@validate_types(**types)` | Runtime type checking for keyword arguments |

### Security

| Decorator | Description |
|-----------|-------------|
| `@sanitize_input` | HTML-escapes all string arguments |
| `@require_authentication(user_dict)` | Checks `authenticated` flag before execution |

### Utilities

| Decorator | Description |
|-----------|-------------|
| `@singleton` | Ensures a class has only one instance |
| `@to_json` | Converts return value to JSON string |
| `@periodic_execution(interval)` | Runs function periodically in a background thread |

### Graylog Logging

| Decorator / Function | Description |
|----------------------|-------------|
| `init_logger(name, graylog_host, log_level)` | Configures loguru with Graylog UDP + console sinks |
| `@log_exceptions(context, enable_raise)` | Logs exceptions to Graylog via loguru |
| `@log_execution_time(context)` | Logs function duration to Graylog |
| `LoggingMiddleware` | FastAPI middleware for request/response logging |

### Periodic Task Scheduler

| Class / Method | Description |
|----------------|-------------|
| `Periodic_task_sched()` | Creates a scheduler instance |
| `.set_database(db_config)` | Configures SQLite or PostgreSQL backend |
| `.periodic_execution(interval, priority, ...)` | Decorator to register periodic tasks |
| `.start_api()` | Launches a FastAPI dashboard (requires `[scheduler]` extras) |
| `.verify_admin(token)` | JWT-based token verification for API routes |

---

## Examples

Check the [`examples/`](examples/) directory for runnable code covering every decorator:

```bash
# Run any example
python examples/benchmark_example.py
python examples/retry_example.py
python examples/timeout_example.py
python examples/singleton_example.py
# ... and many more
```

### Periodic Tasks

```python
from wdecorators import Periodic_task_sched
import time

controller = Periodic_task_sched()
controller.set_database()

@controller.periodic_execution(interval=5, priority="high", enable_api=True)
def critical_task():
    print("Critical task running...")

@controller.periodic_execution(interval=10, priority="medium")
def secondary_task():
    print("Secondary task running...")

critical_task()
secondary_task()
controller.start_api()

time.sleep(60)
```

### Graylog Structured Logging

```python
from wdecorators import init_logger, log_exceptions, logger

init_logger("my_app", graylog_host="192.168.1.100")

@log_exceptions(context={"send_to_graylog": True})
def process_order(order_id: int):
    logger.bind(send_to_graylog=True).info(f"Processing order {order_id}")
    # ... business logic
```

---

## Project Structure

```
wdecorators/
├── wdecorators/
│   ├── __init__.py           # Public API exports
│   ├── general/              # General-purpose decorators
│   │   ├── __init__.py
│   │   ├── benchmark.py
│   │   ├── count_calls.py
│   │   ├── debug_arguments.py
│   │   ├── disk_cache.py
│   │   ├── log_exceptions.py
│   │   ├── log_return.py
│   │   ├── memoize.py
│   │   ├── periodic_execution.py
│   │   ├── profile_memory.py
│   │   ├── rate_limit.py
│   │   ├── require_authentication.py
│   │   ├── retry.py
│   │   ├── retry_on_exception.py
│   │   ├── sanitize_input.py
│   │   ├── silent_fail.py
│   │   ├── singleton.py
│   │   ├── time_execution.py
│   │   ├── timeout.py
│   │   ├── to_json.py
│   │   ├── trace_execution.py
│   │   └── validate_types.py
│   ├── graylog/              # Graylog GELF logging integration
│   │   ├── __init__.py
│   │   ├── handler.py
│   │   ├── loggerg.py
│   │   └── middleware.py
│   ├── log_calls/            # Simple call logging decorator
│   │   └── log_calls.py
│   └── periodic_scheduller/  # Periodic task scheduler with dashboard
│       ├── __init__.py
│       └── controller.py
├── examples/                 # Runnable examples for every decorator
│   ├── benchmark_example.py
│   ├── ...
│   ├── graylog/
│   │   ├── example_fastapi.py
│   │   └── example_script.py
│   └── periodic_task/
│       └── basic.py
├── pyproject.toml
└── README.md
```

---

## Development

```bash
git clone https://github.com/wisrovi/wdecorators.git
cd wdecorators
pip install -e ".[scheduler]"
```

### Code quality

```bash
pip install isort black
isort .
black .
```

---

## License

MIT © [William Steve Rodriguez Villamizar](LICENSE)
