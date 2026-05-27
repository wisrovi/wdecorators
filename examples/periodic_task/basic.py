"""Basic periodic task scheduling example."""

import time

from wdecorators import Periodic_task_sched

controller = Periodic_task_sched()
controller.set_database()


@controller.periodic_execution(interval=5, priority="high", enable_api=True)
def task_critical():
    """Critical task that runs every 5 seconds."""
    print("Executing critical task...")


@controller.periodic_execution(interval=10, priority="medium")
def task_secondary():
    """Secondary task that runs every 10 seconds."""
    print("Executing secondary task...")


task_critical()
task_secondary()

controller.start_api()

try:
    time.sleep(30)
except KeyboardInterrupt:
    print("Stopping tasks...")
