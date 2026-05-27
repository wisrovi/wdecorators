"""Example: singleton decorator - ensure only one class instance."""

from wdecorators import singleton


@singleton
class Database:
    """Simulate a database connection singleton."""

    def __init__(self):
        print("Initializing database connection...")
        self.connected = True


db1 = Database()
db2 = Database()
print(f"db1 is db2: {db1 is db2}")  # True
print(f"db1.connected: {db1.connected}")
