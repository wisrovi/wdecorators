import time

def time_execution(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        print(f"{func.__name__} tomó {elapsed_time:.6f} segundos")
        return result
    return wrapper

@time_execution
def slow_function():
    time.sleep(1)
    return "Listo"

@time_execution
def fast_function():
    return "Rápido!"

print(slow_function())
print(fast_function())
