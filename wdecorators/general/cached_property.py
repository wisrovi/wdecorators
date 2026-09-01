"""Descriptor that caches a property value with optional invalidation."""


class cached_property:
    """A property that caches its result and supports manual invalidation.

    Example:
        .. code-block:: python

           class MyClass:
               @cached_property
               def data(self):
                   print("Loading data...")
                   return load_data()

           obj = MyClass()
           print(obj.data)  # loads
           print(obj.data)  # cached
           del obj.data     # invalidate
           print(obj.data)  # loads again

    """

    def __init__(self, func):
        """Initialize cached_property.

        Args:
            func: Function to wrap as a cached property.
        """
        self.func = func
        self.attr_name = func.__name__

    def __get__(self, instance, owner):
        """Get property value from instance or compute and cache it."""
        if instance is None:
            return self
        try:
            return instance.__dict__[self.attr_name]
        except KeyError:
            value = self.func(instance)
            instance.__dict__[self.attr_name] = value
            return value

    def __delete__(self, instance):
        """Invalidate and delete cached property from instance."""
        try:
            del instance.__dict__[self.attr_name]
        except KeyError:
            pass
