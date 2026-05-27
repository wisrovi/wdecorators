"""Sphinx configuration for wdecorators documentation."""

import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "wdecorators"
copyright = "2026, William Rodriguez"
author = "William Rodriguez"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

autodoc_default_options = {
    "members": True,
    "undoc-members": False,
    "show-inheritance": True,
}
