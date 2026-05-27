"""Tests for cached_property descriptor."""

from wdecorators import cached_property


def test_cached_property_caches_result():
    call_count = [0]

    class MyClass:
        @cached_property
        def value(self):
            call_count[0] += 1
            return 42

    obj = MyClass()
    assert obj.value == 42
    assert call_count[0] == 1
    assert obj.value == 42
    assert call_count[0] == 1


def test_cached_property_invalidation():
    call_count = [0]

    class MyClass:
        @cached_property
        def value(self):
            call_count[0] += 1
            return 42

    obj = MyClass()
    assert obj.value == 42
    assert call_count[0] == 1
    del obj.value
    assert obj.value == 42
    assert call_count[0] == 2


def test_cached_property_different_instances():
    call_count = [0]

    class MyClass:
        @cached_property
        def value(self):
            call_count[0] += 1
            return 42

    obj1 = MyClass()
    obj2 = MyClass()
    assert obj1.value == 42
    assert call_count[0] == 1
    assert obj2.value == 42
    assert call_count[0] == 2


def test_cached_property_class_access():
    class MyClass:
        @cached_property
        def value(self):
            return 42

    assert isinstance(MyClass.value, cached_property)


def test_cached_property_delete_missing():
    class MyClass:
        @cached_property
        def value(self):
            return 42

    obj = MyClass()
    del obj.value


def test_cached_property_computation_reruns_after_delete():
    results = iter([1, 2])

    class MyClass:
        @cached_property
        def value(self):
            return next(results)

    obj = MyClass()
    assert obj.value == 1
    del obj.value
    assert obj.value == 2
