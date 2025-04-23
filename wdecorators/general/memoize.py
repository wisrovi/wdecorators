import functools

def memoize(func):
    cache = {}

    @functools.wraps(func)
    def wrapper(*args):
        if args in cache:
            return cache[args]
        result = func(*args)
        cache[args] = result
        return result
    return wrapper

@memoize
def slow_square(n):
    import time
    time.sleep(5)
    return n * n

print(slow_square(4))  # Primera vez, lento
print(slow_square(4))  # Segunda vez, instantáneo
