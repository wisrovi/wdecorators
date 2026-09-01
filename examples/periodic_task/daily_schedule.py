"""Example demonstrating specific daily execution scheduling using run_at parameter."""

from wdecorators import Periodic_task_sched

# Initialize controller with auto database handler and signal registration
controller: Periodic_task_sched = Periodic_task_sched(
    auto_database=True, handle_signals=True
)


@controller.periodic_execution(
    run_at=["04:00", "10:00", "16:00", "23:59"], priority="high", enable_api=True
)
def generate_daily_reports() -> None:
    """Generate scheduled system reports at specific times of day.

    Executes daily at 04:00, 10:00, 16:00, and 23:59.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("[Task: Report] Generating scheduled system report...")


@controller.periodic_execution(run_at="02:00", priority="medium")
def nightly_database_backup() -> None:
    """Run database backup every night at 02:00 AM.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("[Task: Backup] Running nightly database backup...")


def main() -> None:
    """Main execution function to launch daily scheduled tasks.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    # Start tasks
    generate_daily_reports()
    nightly_database_backup()

    # Start FastAPI dashboard on http://localhost:8000
    controller.start_api()

    # Block main thread safely and handle SIGINT / SIGTERM gracefully
    controller.run_forever()


if __name__ == "__main__":
    main()
