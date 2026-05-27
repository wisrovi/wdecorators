"""Example: ignore_kwargs decorator - ignore specific kwargs."""

from wdecorators import ignore_kwargs


@ignore_kwargs("unused", "deprecated_opt")
def process(data):
    return f"Processing: {data}"


print(process("test", unused="ignored", deprecated_opt="also ignored"))
