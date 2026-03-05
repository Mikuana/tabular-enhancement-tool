import os
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

with open(os.path.abspath("../pyproject.toml"), "rb") as f:
    pyproject = tomllib.load(f)

project_data = pyproject.get("project", {})
project = project_data.get("name", "Tabular-Enhancement-Tool")
author_list = project_data.get("authors", [])
author = ", ".join([a.get("name", "") for a in author_list if "name" in a])
release = project_data.get("version", "0.2.2")
# noinspection PyShadowingBuiltins
copyright = f"2026, {author}"

sys.path.insert(0, os.path.abspath(".."))

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

myst_url_schemes = ("http", "https", "mailto", "ftp")
# To fix: WARNING: 'myst' cross-reference target not found: 'LICENSE'
# We want these to be treated as standard links, not cross-references.
# Files that are not part of the toctree should be handled as links to files.
# By default MyST tries to resolve [text](file) as a cross-reference.

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "sphinx_rtd_theme"
# sphinx-autodoc-typehints configuration
set_type_checking_flag = True
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True
# If you still get warnings about forward references,
# you can tell the extension to ignore them.
typehints_defaults = "comma"

# Suppress the specific forward reference warning
suppress_warnings = [
    "sphinx_autodoc_typehints.forward_reference",
]
