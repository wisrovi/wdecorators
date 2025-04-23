def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

@singleton
class Database:
    def __init__(self):
        print("Conectando a la base de datos...")

db1 = Database()
db2 = Database()
print(db1 is db2)  # True, porque es un singleton
