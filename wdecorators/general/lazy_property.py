"""Descriptor that lazily computes and caches a property value."""


class lazy_property:
    """A property that is computed once on first access and then cached.

    Unlike functools.cached_property, this works on Python 3.7+.

    Example:
        .. code-block:: python

           class MyClass:
               @lazy_property
               def config(self):
                   print("Loading config...")
                   return {"key": "value"}

    """

    def __init__(self, func):
        """Initialize lazy_property.

        Args:
            func: Function to wrap as a lazy property.
        """
        self.func = func
        self.attr_name = func.__name__

    def __get__(self, instance, owner):
        """Get property value from instance or compute lazily."""
        if instance is None:
            return self
        value = self.func(instance)
        setattr(instance, self.attr_name, value)
        return value
