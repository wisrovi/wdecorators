import functools


def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Llamando a {func.__name__} con args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} retornó {result}")
        return result

    return wrapper


@log_calls
def add(a, b):
    return a + b


@log_calls
def greet(name):
    return f"Hola, {name}!"


print(add(2, 3))
print(greet("Alice"))
