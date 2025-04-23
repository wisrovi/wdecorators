import functools

def validate_types(**expected_types):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for arg_name, arg_value in kwargs.items():
                if arg_name in expected_types and not isinstance(arg_value, expected_types[arg_name]):
                    raise TypeError(f"Argumento {arg_name} debe ser de tipo {expected_types[arg_name]}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@validate_types(name=str, age=int)
def person_info(name, age):
    return f"{name} tiene {age} años"

print(person_info(name="Carlos", age=30))
# print(person_info(name="Carlos", age="treinta"))  # Esto lanzará un TypeError
