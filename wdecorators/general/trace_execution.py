import functools

def trace_execution(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Entrando en {func.__name__}")
        result = func(*args, **kwargs)
        print(f"Saliendo de {func.__name__}")
        return result
    return wrapper

@trace_execution
def multiply(a, b):
    return a * b

@trace_execution
def greet(name):
    return f"Hola, {name}!"

print(multiply(3, 4))
print(greet("Carlos"))
