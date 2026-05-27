"""Tests for sanitize_input decorator."""

from wdecorators import sanitize_input


def test_sanitize_input_escapes_string():
    @sanitize_input
    def show(message):
        return message

    result = show("<script>alert('XSS')</script>")
    assert result == "&lt;script&gt;alert(&#x27;XSS&#x27;)&lt;/script&gt;"


def test_sanitize_input_passes_non_string():
    @sanitize_input
    def show(count):
        return count

    result = show(42)
    assert result == 42


def test_sanitize_input_escapes_kwargs():
    @sanitize_input
    def show(message, title):
        return f"{title}: {message}"

    result = show("<b>bold</b>", title="<i>title</i>")
    assert result == "&lt;i&gt;title&lt;/i&gt;: &lt;b&gt;bold&lt;/b&gt;"


def test_sanitize_input_mixed_args():
    @sanitize_input
    def show(name, value):
        return f"{name}: {value}"

    result = show("<script>", 42)
    assert result == "&lt;script&gt;: 42"
