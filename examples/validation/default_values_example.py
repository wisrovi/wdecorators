"""Example: default_values decorator - set default kwargs."""

from wdecorators import default_values


@default_values(timeout=30, retries=3, verbose=False)
def connect(host, port, timeout=None, retries=None, verbose=None):
    return {
        "host": host,
        "port": port,
        "timeout": timeout,
        "retries": retries,
        "verbose": verbose,
    }


print(connect("localhost", 8080))
print(connect("example.com", 443, timeout=60))
