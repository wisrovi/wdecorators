import time
import functools

def retry_on_exception(retries=3, delay=2, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"Intento {i+1} falló: {e}. Reintentando en {delay} segundos...")
                    time.sleep(delay)
            raise RuntimeError(f"La función {func.__name__} falló después de {retries} intentos.")
        return wrapper
    return decorator


@retry_on_exception(retries=3, delay=2, exceptions=(ZeroDivisionError,))
def risky_function(x):
    if x == 0:
        raise ZeroDivisionError("División entre cero!")
    return 10 / x



risky_function(0)