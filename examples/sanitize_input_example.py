"""Example: sanitize_input decorator - HTML-escape string arguments."""

from wdecorators import sanitize_input


@sanitize_input
def display_message(message: str) -> str:
    """Display a message with sanitized input."""
    return f"Message: {message}"


print(display_message("<script>alert('XSS')</script>"))
# Output: Message: &lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;
