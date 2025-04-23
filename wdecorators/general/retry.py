import functools

def retry(times=3):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    print(f"Fallo {func.__name__}, reintentando... Error: {e}")
            return None
        return wrapper
    return decorator

@retry(times=5)
def may_fail():
    import random
    if random.random() < 0.7:
        raise ValueError("Falló la ejecución")
    return "Éxito"

print(may_fail())
