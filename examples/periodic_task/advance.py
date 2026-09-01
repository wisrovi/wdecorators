"""Advanced periodic task scheduling example with automatic signals, DB initialization, and run_forever loop."""

from wdecorators import Periodic_task_sched

# Initialize controller with auto_database=True and handle_signals=True
controller: Periodic_task_sched = Periodic_task_sched(
    auto_database=True, handle_signals=True
)


@controller.periodic_execution(
    interval=3,
    priority="high",
    max_executions=5,
    dynamic_interval=True,
    enable_api=True,
)
def fetch_data() -> None:
    """Fetch initial data batch (runs up to 5 times).

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("[Task: Fetch] Fetching latest data batch...")


@controller.periodic_execution(
    interval=5, priority="medium", adaptive_priority=True, dependent_task="fetch_data"
)
def process_data() -> None:
    """Process data only after fetch_data has executed.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("[Task: Process] Processing fetched data...")


def main() -> None:
    """Main execution function to launch periodic tasks and API server.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    # Start periodic tasks
    fetch_data()
    process_data()

    # Start the monitoring API dashboard (accessible at http://localhost:8000)
    controller.start_api()

    # Block main thread safely; handles KeyboardInterrupt & SIGINT/SIGTERM internally
    controller.run_forever()


if __name__ == "__main__":
    main()
