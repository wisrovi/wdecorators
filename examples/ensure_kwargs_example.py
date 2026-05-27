"""Example: ensure_kwargs decorator - force keyword arguments."""

from wdecorators import ensure_kwargs


@ensure_kwargs
def connect(*, host, port):
    return f"Connected to {host}:{port}"


# Works with positional args thanks to @ensure_kwargs
print(connect("localhost", 8080))
print(connect(host="example.com", port=443))
