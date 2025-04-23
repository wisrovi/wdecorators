import functools

def debug_arguments(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Llamado a {func.__name__} con args={args}, kwargs={kwargs}")
        return func(*args, **kwargs)
    return wrapper

@debug_arguments
def add(a, b):
    return a + b

@debug_arguments
def greet(name="Mundo"):
    return f"Hola, {name}!"

print(add(5, 10))
print(greet(name="Carlos"))
