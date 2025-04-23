import functools

def count_calls(func):
    func.call_count = 0

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        func.call_count += 1
        print(f"{func.__name__} ha sido llamada {func.call_count} veces")
        return func(*args, **kwargs)
    return wrapper

@count_calls
def say_hello():
    return "Hola!"

@count_calls
def add(a, b):
    return a + b

print(say_hello())
print(say_hello())
print(add(1, 2))
print(add(3, 4))
