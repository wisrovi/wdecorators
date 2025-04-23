import functools
import tracemalloc

def profile_memory(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        result = func(*args, **kwargs)
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        print(f"Memoria usada: actual={current}, pico={peak}")
        return result
    return wrapper

@profile_memory
def create_list():
    return [i for i in range(100000)]

@profile_memory
def small_list():
    return [1, 2, 3]

print(create_list())
print(small_list())
