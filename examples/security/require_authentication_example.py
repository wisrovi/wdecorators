"""Example: require_authentication decorator - protect functions."""

from wdecorators import require_authentication

user = {"authenticated": True}


@require_authentication(user)
def secret_info() -> str:
    """Return sensitive information (requires authentication)."""
    return "This is secret information"


print(secret_info())  # Works

# Try with unauthenticated user
user["authenticated"] = False
try:
    secret_info()
except PermissionError as e:
    print(f"Access denied: {e}")
