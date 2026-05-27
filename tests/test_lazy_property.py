"""Tests for lazy_property descriptor."""

from wdecorators import lazy_property


def test_lazy_property():
    call_count = [0]

    class MyClass:
        @lazy_property
        def value(self):
            call_count[0] += 1
            return 42

    obj = MyClass()
    assert obj.value == 42
    assert call_count[0] == 1
    assert obj.value == 42  # Cached
    assert call_count[0] == 1


def test_lazy_property_different_instances():
    class MyClass:
        @lazy_property
        def value(self):
            return id(self)

    a, b = MyClass(), MyClass()
    assert a.value == a.value
    assert b.value == b.value
    assert a.value != b.value


def test_lazy_property_class_access():
    class MyClass:
        @lazy_property
        def value(self):
            return 42

    descriptor = MyClass.__dict__["value"]
    assert MyClass.value is descriptor
