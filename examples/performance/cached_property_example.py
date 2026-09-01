"""Example: cached_property decorator with invalidation."""

from wdecorators import cached_property


class DataStore:
    @cached_property
    def data(self):
        print("Fetching data...")
        return [1, 2, 3, 4, 5]


store = DataStore()
print(store.data)  # Fetches
print(store.data)  # Cached

del store.data  # Invalidate
print(store.data)  # Fetches again
