"""Production-grade periodic task scheduling example combining resilience, benchmarking, error logging, and task dependencies."""

import random

from wdecorators import (
    Periodic_task_sched,
    benchmark,
    count_calls,
    log_exceptions,
    retry,
    silent_fail,
    time_execution,
)

# Initialize the scheduler controller with automatic SQLite DB & signal handlers
controller: Periodic_task_sched = Periodic_task_sched(
    auto_database=True, handle_signals=True
)


@controller.periodic_execution(
    interval=4,
    priority="high",
    max_executions=6,
    dynamic_interval=True,
    enable_api=True,
)
@time_execution
@retry(times=3)
@count_calls
def fetch_external_api() -> None:
    """Fetch data from an external API with automatic retries and timing.

    Simulates an HTTP request to an external service that may experience
    transient network errors.

    Args:
        None

    Returns:
        None

    Raises:
        ConnectionError: If a simulated transient network glitch occurs.
    """
    print("[Task: Fetch] Requesting payload from external service...")
    if random.random() < 0.3:
        print("[Task: Fetch] Simulating transient network glitch...")
        raise ConnectionError("Temporary connection timeout")
    print("[Task: Fetch] Data successfully received.")


@controller.periodic_execution(
    interval=8,
    priority="medium",
    adaptive_priority=True,
    dependent_task="fetch_external_api",
)
@benchmark
@log_exceptions()
def process_analytics_batch() -> None:
    """Process analytics batch dependent on fetch_external_api.

    Transforms and stores incoming data once the dependent fetch task has completed.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("[Task: Analytics] Transforming and storing analytics batch...")


@controller.periodic_execution(interval=12, priority="low")
@silent_fail
def cleanup_temp_cache() -> None:
    """Periodically purge temporary cache files.

    Cleans up temporary IO files and ignores non-critical errors.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("[Task: Cleanup] Sweeping temporary cache files...")


def main() -> None:
    """Main execution function to register and launch all periodic tasks.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    # Start periodic task execution threads
    fetch_external_api()
    process_analytics_batch()
    cleanup_temp_cache()

    # Start the FastAPI dashboard on http://localhost:8000
    controller.start_api()

    # Block main thread safely and handle SIGINT / SIGTERM gracefully
    controller.run_forever()


if __name__ == "__main__":
    main()
