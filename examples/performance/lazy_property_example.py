"""Example: lazy_property decorator - lazy property evaluation."""

from wdecorators import lazy_property


class Config:
    @lazy_property
    def settings(self):
        print("Loading settings...")
        return {"host": "localhost", "port": 8080}


cfg = Config()
print(cfg.settings)  # Loads
print(cfg.settings)  # Cached (no "Loading" message)
print(cfg.settings["host"])
