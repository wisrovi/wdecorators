from typing import Any, Dict


def singleton(cls: type) -> type:
    """Decorator that ensures a class has only one instance (singleton pattern)."""
    instances: Dict[type, Any] = {}

    def get_instance(*args: Any, **kwargs: Any) -> Any:
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
