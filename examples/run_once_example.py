"""Example: run_once decorator - execute function only once."""

from wdecorators import run_once


@run_once
def initialize():
    print("Initializing...")
    return {"status": "ready"}


print(initialize())  # Runs: prints "Initializing..." and returns dict
print(initialize())  # Cached: returns dict without printing
print(initialize())  # Cached again
