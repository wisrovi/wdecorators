import functools
import pickle
import os

def disk_cache(filename="cache.pkl"):
    def decorator(func):
        cache = {}
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                cache = pickle.load(f)

        @functools.wraps(func)
        def wrapper(*args):
            if args in cache:
                return cache[args]
            result = func(*args)
            cache[args] = result
            with open(filename, "wb") as f:
                pickle.dump(cache, f)
            return result
        return wrapper
    return decorator

@disk_cache("square_cache.pkl")
def square(n):
    return n * n

print(square(5))
print(square(5))  # Esto lo leerá del archivo
