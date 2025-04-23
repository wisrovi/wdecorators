import functools

def require_authentication(user):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not user.get("authenticated", False):
                raise PermissionError("Acceso denegado")
            return func(*args, **kwargs)
        return wrapper
    return decorator

user = {"authenticated": True}

@require_authentication(user)
def secret_info():
    return "Información secreta"

print(secret_info())
