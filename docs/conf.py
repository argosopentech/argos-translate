import sphinx_rtd_theme

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import ast
from pathlib import Path
import os
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
# Documentation builds must not initialize downloadable sentence splitters.
os.environ["ARGOS_CHUNK_TYPE"] = "NONE"


# -- Project information -----------------------------------------------------

project = 'Argos Translate'
copyright = '2020, Argos Open Technologies, LLC'
author = 'Argos Open Technologies, LLC'

# The full version, including alpha/beta/rc tags
# Read the version from source so branch builds do not report an installed release.
setup_tree = ast.parse((ROOT / "setup.py").read_text())
release = next(
    keyword.value.value
    for node in ast.walk(setup_tree)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    and node.func.id == "setup"
    for keyword in node.keywords if keyword.arg == "version"
)
version = release


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx_rtd_theme",
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = []

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
# html_theme = 'alabaster'
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

linkcheck_timeout = 15
linkcheck_retries = 2
linkcheck_anchors = False
