import time
import functools

def benchmark(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} tomó {elapsed:.6f} segundos")
        return result
    return wrapper

@benchmark
def slow_task():
    time.sleep(2)
    return "Completado"

@benchmark
def quick_task():
    return "Listo"

print(slow_task())
print(quick_task())
