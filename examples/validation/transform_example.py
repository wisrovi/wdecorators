"""Example: transform decorator - transform return values."""

from wdecorators import transform


@transform(str.strip)
@transform(str.lower)
def get_name():
    return "  ALICE  "


print(repr(get_name()))  # 'alice'
