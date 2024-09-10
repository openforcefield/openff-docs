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


# -- Project information -----------------------------------------------------

project = "OpenFF Documentation"
copyright = "2022, The Open Force Field Initiative"
author = "The Open Force Field Initiative"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.mathjax",
    "sphinx.ext.intersphinx",
    # "nbsphinx",
    "myst_nb",
    "openff_sphinx_theme",
    "sphinx_design",
]
source_suffix = [".rst", ".md"]
# Extensions for the myst parser
myst_enable_extensions = [
    "dollarmath",
    "colon_fence",
    "smartquotes",
    "replacements",
    "deflist",
    "attrs_inline",
    "attrs_block",
]
myst_url_schemes = (
    "mailto",
    "http",
    "https",
)
suppress_warnings = [
    "myst.header",
]
_python_doc_base = "https://docs.python.org/3.6"
intersphinx_mapping = {
    "python": ("https://docs.python.org/3.6", None),
    "numpy": ("https://numpy.org/doc/stable", None),
    "scipy": ("https://docs.scipy.org/doc/scipy/reference", None),
    "scikit.learn": ("https://scikit-learn.org/stable", None),
    "openmm": ("http://docs.openmm.org/latest/api-python/", None),
    "rdkit": ("https://www.rdkit.org/docs", None),
    "openeye": ("https://docs.eyesopen.com/toolkits/python/", None),
    "mdtraj": ("https://www.mdtraj.org/1.9.5/", None),
    "conda": ("https://docs.conda.io/projects/conda/en/latest", None),
    "mamba": ("https://mamba.readthedocs.io/en/latest/", None),
    "openff.toolkit": ("https://docs.openforcefield.org/toolkit/en/stable", None),
    "openff.interchange": (
        "https://docs.openforcefield.org/interchange/en/stable",
        None,
    ),
    "openff.units": ("https://docs.openforcefield.org/units/en/stable", None),
    "openff.bespokefit": ("https://docs.openforcefield.org/bespokefit/en/stable", None),
    "openff.qcsubmit": ("https://docs.openforcefield.org/qcsubmit/en/stable", None),
    "openff.fragmenter": ("https://docs.openforcefield.org/fragmenter/en/stable", None),
    "openff.evaluator": ("https://docs.openforcefield.org/evaluator/en/stable", None),
    "openff.recharge": ("https://docs.openforcefield.org/recharge/en/stable", None),
    "openff.nagl": ("https://docs.openforcefield.org/nagl/en/stable", None),
}
intersphinx_disabled_reftypes = ["*"]
myst_heading_anchors = 2

sd_custom_directives = {
    "faq-entry": {
        "inherit": "dropdown",
        "options": {
            "animate": "fade-in-slide-down",
            "class-container": "faq",
        },
    }
}

# sphinx-notfound-page
# https://github.com/readthedocs/sphinx-notfound-page
# Renders a 404 page with absolute links
import importlib

if importlib.util.find_spec("notfound"):
    extensions.append("notfound.extension")

    notfound_context = {
        "title": "404: File Not Found",
        "body": """
    <h1>404: File Not Found</h1>
    <p>
        Sorry, we couldn't find that page. Try using the search box or the
        navigation menu on the left.
    </p>
    <p>
    </p>
    """,
    }

extensions.append("sphinxawesome.codelinter")
codelinter_languages = {
    # Language: command to pass codeblock as stdin
    "python": "python source/_ext/check_python_codeblocks.py",
}
# Tell MyST-NB about codelinter builder
nb_mime_priority_overrides = [
    ("codelinter", "text/plain", 0),
]

# Configure the linkcheck builder
linkcheck_anchors = False  # This generates lots of false positives
linkcheck_ignore = [
    r'https://pubs.acs.org/doi/' # ACS 403s the link checker. Thanks ACS.
]

# Cookbook stuff
import sys
from pathlib import Path

sys.path.insert(0, str(Path("./_ext").resolve()))
extensions.extend(
    [
        "cookbook.sphinx_ext",
    ]
)
nbsphinx_execute = "never"
nb_execution_mode = "off"
# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]
html_static_path = ["_static"]
html_css_files = [
    "css/deflist-flowchart.css",
    "css/cookbook.css",
    "css/faq.css",
]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "Thumbs.db",
    ".DS_Store",
    "_*",
    # Don't render colab notebooks
    "workshops/2024/protein_prep/colab-protein_prep.ipynb",
    "workshops/2024/smirnoff/colab-smirnoff.ipynb",
    "workshops/2024/vignettes/colab-vignettes.ipynb",
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "openff_sphinx_theme"

# (Optional) Logo and favicon
# html_logo = "_static/images/logos/openff_toolkit_v1_white.png"
# html_favicon = "_static/images/favicon.svg"

# Theme options are theme-specific and customize the look and feel of a
# theme further.
html_theme_options = {
    # Colour for sidebar captions and other accents. One of
    # openff-toolkit-blue, openff-dataset-yellow, openff-evaluator-orange,
    # red, pink, purple, deep-purple, indigo, blue, light-blue, cyan,
    # teal, green, light-green, lime, yellow, amber, orange, deep-orange
    "color_accent": "openff-toolkit-blue",
    # Content Minification for deployment, prettification for debugging
    "html_minify": False,
    "html_prettify": False,
    "css_minify": True,
    "master_doc": False,
}

# Custom sidebar templates, must be a dictionary that maps document names
# to template names.
html_sidebars = {
    "**": ["globaltoc.html", "searchbox.html", "localtoc.html"],
}
