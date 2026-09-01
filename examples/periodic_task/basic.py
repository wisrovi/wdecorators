"""Basic periodic task scheduling example."""

import time

from wdecorators import Periodic_task_sched

controller: Periodic_task_sched = Periodic_task_sched()
controller.set_database()


@controller.periodic_execution(interval=5, priority="high", enable_api=True)
def task_critical() -> None:
    """Critical task that runs every 5 seconds.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("Executing critical task...")


@controller.periodic_execution(interval=10, priority="medium")
def task_secondary() -> None:
    """Secondary task that runs every 10 seconds.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    print("Executing secondary task...")


def main() -> None:
    """Main function to launch basic periodic tasks.

    Args:
        None

    Returns:
        None

    Raises:
        None
    """
    task_critical()
    task_secondary()

    controller.start_api()

    try:
        time.sleep(30)
    except KeyboardInterrupt:
        print("Stopping tasks...")


if __name__ == "__main__":
    main()
