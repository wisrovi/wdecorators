import time
import functools

def rate_limit(calls_per_second):
    interval = 1.0 / calls_per_second
    last_call = [0]

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_call[0]
            if elapsed < interval:
                time.sleep(interval - elapsed)
            last_call[0] = time.time()
            return func(*args, **kwargs)
        return wrapper
    return decorator

@rate_limit(2)  # Máximo 2 llamadas por segundo
def say_hello():
    print("Hola!")

say_hello()
say_hello()
say_hello()
say_hello()
say_hello()
say_hello()
say_hello()
say_hello()
say_hello()
say_hello()
