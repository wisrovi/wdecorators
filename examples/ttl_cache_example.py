"""Example: ttl_cache decorator - time-to-live cache."""

import time
from wdecorators import ttl_cache


@ttl_cache(seconds=2, maxsize=5)
def get_data(key):
    print(f"Computing data for '{key}'...")
    return f"value-{key}"


print(get_data("a"))  # Computes
print(get_data("a"))  # Cached
time.sleep(3)
print(get_data("a"))  # Expired, computes again
print(get_data("b"))  # Computes new
