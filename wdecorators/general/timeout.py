import signal
import functools

class TimeoutException(Exception):
    pass

def timeout(seconds):
    def decorator(func):
        def handler(signum, frame):
            raise TimeoutException("Tiempo excedido!")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(seconds)
            try:
                return func(*args, **kwargs)
            finally:
                signal.alarm(0)
        return wrapper
    return decorator

@timeout(2)
def long_task():
    import time
    time.sleep(3)
    return "Terminado"

print(long_task())  # Esto lanzará TimeoutException
