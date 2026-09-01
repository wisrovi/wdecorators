"""Example: coerce_types decorator - coerce argument types."""

from wdecorators import coerce_types


@coerce_types(age=int, active=bool)
def process(age, active):
    return (
        f"age={age} ({type(age).__name__}), active={active} ({type(active).__name__})"
    )


print(process(age="25", active="true"))
print(process(age=30, active=1))
