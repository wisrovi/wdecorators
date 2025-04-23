import functools
import html

def sanitize_input(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        clean_args = [html.escape(str(arg)) for arg in args]
        clean_kwargs = {k: html.escape(str(v)) for k, v in kwargs.items()}
        return func(*clean_args, **clean_kwargs)
    return wrapper

@sanitize_input
def display_message(message):
    return f"Mensaje: {message}"

print(display_message("<script>alert('Hacked!')</script>"))
