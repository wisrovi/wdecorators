"""Comprehensive example demonstrating cron scheduling, async tasks, overlap prevention, callbacks, thread pools, and Prometheus metrics."""

import asyncio
from typing import Any

from wdecorators import Periodic_task_sched

# Initialize controller with thread pool (max_workers=5), auto DB & signal handling
controller: Periodic_task_sched = Periodic_task_sched(
    auto_database=True, handle_signals=True, max_workers=5
)


def handle_success(result: Any) -> None:
    """Callback executed when a task succeeds.

    Args:
        result: Return value of the task function.

    Returns:
        None

    Raises:
        None
    """
    print(f"[Callback: Success] Task completed successfully: {result}")


def handle_error(error: Exception) -> None:
    """Callback executed when a task fails with an exception.

    Args:
        error: Exception raised during task execution.

    Returns:
        None

    Raises:
        None
    """
    print(f"[Callback: Error] Task encountered an error: {error}")


@controller.periodic_execution(
    cron="*/1 * * * *",
    priority="high",
    allow_concurrent=False,
    on_success=handle_success,
    on_error=handle_error,
    enable_api=True,
)
async def async_cron_task() -> str:
    """Asynchronous task running on a 1-minute cron schedule.

    Prevents overlapping executions if the task takes longer than the interval.

    Args:
        None

    Returns:
        Confirmation message string.

    Raises:
        None
    """
    print("[Task: Async Cron] Starting async processing...")
    await asyncio.sleep(0.5)
    print("[Task: Async Cron] Async task finished.")
    return "Async cron process completed"


@controller.periodic_execution(
    interval=5,
    priority="medium",
    allow_concurrent=False,
    on_success=handle_success,
    on_error=handle_error,
)
def sync_interval_task() -> int:
    """Synchronous task with overlap prevention and callbacks.

    Args:
        None

    Returns:
        Processed count integer.

    Raises:
        None
    """
    print("[Task: Sync Interval] Executing synchronous workload...")
    return 42


def main() -> None:
    """Main execution function to launch all full-featured tasks.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    # Start tasks
    async_cron_task()
    sync_interval_task()

    # Start FastAPI dashboard with /metrics Prometheus endpoint at http://localhost:8000
    controller.start_api()

    # Block main thread safely and handle SIGINT / SIGTERM gracefully
    controller.run_forever()


if __name__ == "__main__":
    main()
