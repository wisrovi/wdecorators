"""Example: wait_until decorator - wait for condition before executing."""

import time

from wdecorators import wait_until

ready = False


def is_ready():
    return ready


@wait_until(is_ready, timeout=5)
def process():
    return "Data processed"


# Start a thread to set ready after 1 second
import threading


def set_ready():
    time.sleep(1)
    global ready
    ready = True


threading.Thread(target=set_ready, daemon=True).start()

result = process()
print(result)
