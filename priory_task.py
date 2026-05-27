"""Example: Periodic tasks with dependencies."""

import time

from wdecorators import Periodic_task_sched

controller = Periodic_task_sched()
controller.set_database()


@controller.periodic_execution(interval=5, priority="high", enable_api=True)
def task_primary():
    """Primary task that runs every 5 seconds."""
    print("Primary task executing...")


@controller.periodic_execution(
    interval=10, priority="medium", dependent_task="task_primary"
)
def task_dependent():
    """Dependent task that runs only after task_primary completes."""
    print("Dependent task executing after primary task...")


task_primary()
task_dependent()

controller.start_api()

try:
    time.sleep(30)
except KeyboardInterrupt:
    print("Stopping tasks...")
