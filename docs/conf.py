import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "Tabular-Enhancement-Tool"
copyright = "2026, Junie"
author = "Junie"
release = "0.1.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
    "sphinx_rtd_theme",
    "myst_parser",
]

# MyST settings (to support README.md with Sphinx)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
# sphinx-autodoc-typehints configuration
set_type_checking_flag = True
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True
# If you still get warnings about SQLAlchemy forward references,
# you can tell the extension to ignore them.
typehints_defaults = "comma"

# Suppress the specific SQLAlchemy forward reference warning
suppress_warnings = ["sphinx_autodoc_typehints.forward_reference"]
