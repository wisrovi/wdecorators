
<img width="1035" height="587" alt="image" src="https://github.com/user-attachments/assets/51127189-cd78-4c57-9e9f-5257ee48f7df" />


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
| `Periodic_task_sched(auto_database, handle_signals, max_workers)` | Creates a scheduler instance with auto DB, signals, and thread pool |
| `.set_database(db_config)` | Configures SQLite or PostgreSQL backend |
| `.periodic_execution(interval, run_at, cron, allow_concurrent, on_success, on_error)` | Decorator to register periodic tasks with cron, async, & callbacks |
| `.start_api()` | Launches FastAPI dashboard and `/metrics` Prometheus endpoint |
| `.stop_all()` | Stops all registered running task executors and thread pools |
| `.run_forever(poll_interval)` | Safely blocks main thread and handles graceful shutdown on interrupt |
| `.verify_admin(token)` | JWT-based token verification for API routes |

---

## Examples

Check the [`examples/`](examples/) directory for runnable code covering every decorator:

```bash
# Run any example
python examples/performance/benchmark_example.py
python examples/resilience/retry_example.py
python examples/periodic_task/full_featured.py
# ... and many more organized by category
```

### Periodic Tasks

```python
from wdecorators import Periodic_task_sched
import asyncio

controller = Periodic_task_sched(auto_database=True, handle_signals=True, max_workers=5)

@controller.periodic_execution(cron="*/1 * * * *", allow_concurrent=False, enable_api=True)
async def async_cron_task():
    print("Async cron task running...")
    await asyncio.sleep(1)

@controller.periodic_execution(run_at=["04:00", "12:00", "20:00"])
def daily_reports():
    print("Daily report task running...")

async_cron_task()
daily_reports()
controller.start_api()

controller.run_forever()
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
│   ├── graylog/              # Graylog GELF logging integration
│   ├── log_calls/            # Simple call logging decorator
│   └── periodic_scheduller/  # Periodic task scheduler with dashboard & metrics
│       ├── __init__.py
│       └── controller.py
├── examples/                 # Categorized runnable examples
│   ├── debugging/            # Debugging and tracing examples
│   ├── graylog/              # Graylog integration examples
│   ├── performance/          # Benchmarking and caching examples
│   ├── periodic_task/        # Periodic task scheduler examples (basic, advance, daily_schedule, full_featured)
│   ├── resilience/           # Retry, timeout, rate-limiting examples
│   ├── security/             # Input sanitization and authentication examples
│   ├── utilities/            # Singleton, JSON, run_once examples
│   └── validation/           # Runtime type & length validation examples
├── pyproject.toml
└── README.md
```

---

## Key Technologies

- **Python 3.8+**: Core runtime.
- **FastAPI & Uvicorn**: Web dashboard and server for monitoring periodic task schedulers.
- **PyJWT & Jinja2**: Authentication and templating for scheduler dashboard.
- **Loguru**: Advanced logging engine with Graylog GELF support.
- **SQLite / PostgreSQL**: Database backends for task logging and execution history.
- **Pytest & Coverage**: Unit testing framework and test coverage reporting.

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
