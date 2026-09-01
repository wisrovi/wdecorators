"""Example: conditional decorator - conditional execution."""

from wdecorators import conditional

feature_enabled = True


@conditional(lambda: feature_enabled)
def experimental():
    return "Experimental feature ran"


print(experimental())  # Runs

feature_enabled = False
print(experimental())  # None (skipped)
