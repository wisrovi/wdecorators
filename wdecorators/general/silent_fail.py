import functools

def silent_fail(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return None
    return wrapper

@silent_fail
def risky_operation():
    return 1 / 0

@silent_fail
def safe_operation():
    return "Todo bien"

print(risky_operation())  # No lanza error, solo retorna None
print(safe_operation())
