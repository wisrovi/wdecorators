import functools

def log_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error en {func.__name__}: {e}")
            return None
    return wrapper

@log_exceptions
def divide(a, b):
    return a / b

@log_exceptions
def fail():
    raise ValueError("¡Algo salió mal!")

print(divide(10, 2))
print(divide(10, 0))
print(fail())
