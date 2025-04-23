import functools

def log_return(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"{func.__name__} retornó {result}")
        return result
    return wrapper

@log_return
def square(n):
    return n * n

@log_return
def hello():
    return "Hola mundo"

print(square(4))
print(hello())
