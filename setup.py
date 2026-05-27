try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    # pip install tomli
    import tomli as tomllib  # Python <3.11

from pathlib import Path

from setuptools import find_packages, setup

with open("pyproject.toml", "rb") as f:
    config = tomllib.load(f)

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name=config["project"]["name"],
    version=config["project"]["version"],
    packages=find_packages(),
    install_requires=["loguru>=0.7.0"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Build Tools",
        "Intended Audience :: Developers",
    ],
    description=config["project"]["description"],
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/wisrovi/wdecorators",
    author="William Steve Rodriguez Villamizar",
    author_email="wisrovi.rodriguez@gmail.com",
    license="MIT",
    python_requires=">=3.7",
)
