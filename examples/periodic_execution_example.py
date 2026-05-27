"""Example: periodic_execution decorator - run a function periodically."""

import time

from wdecorators import periodic_execution


@periodic_execution(interval=3)
def print_heartbeat():
    """Print a heartbeat message every 3 seconds."""
    print("Heartbeat...")


thread = print_heartbeat()
time.sleep(7)  # Let it run for 7 seconds
thread.stop_event.set()  # Stop the periodic execution
print("Done")
