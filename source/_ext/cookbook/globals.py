"""
Global constants for the Sphinx extension and proc_examples.py

These are here to form a quasi-configuration file, rather than have constants
strewn across different modules.
"""
from typing import Final
from pathlib import Path

PACKAGED_ENV_NAME: Final = Path("environment.yaml")
"""
Name of the Conda environment file in zipped download files and Colab folders.
"""

OPENFF_DOCS_ROOT = Path(__file__).parent.parent.parent.parent
"""Path to the root of the openff-docs repo."""

UNIVERSAL_ENV_PATH: Final = OPENFF_DOCS_ROOT / "devtools/conda-envs/examples_env.yml"
"""
Path to the default environment file for notebooks that don't package their own.
"""

IGNORED_FILES: Final = [
    ".gitignore",
    "Thumbs.db",
    ".DS_Store",
    "thumbnail.png",
    "__pycache__",
]
"""File names to exclude from zipped download files and Colab folders."""

GITHUB_REPOS: Final = [
    "openforcefield/openff-toolkit",
    "openforcefield/openff-interchange",
]
"""
GitHub repos to download example notebooks from.

Should be given as ``username/repo-name``.
"""

DO_NOT_SEARCH = [
    "deprecated",
    "external",  # TODO: Do we really want to skip these?
]
"""Directory names to not descend into when searching for notebooks."""

COOKBOOK_DATA_ROOT: Final[Path] = OPENFF_DOCS_ROOT / "source/_cookbook/"
"""
Folder to store the output of proc_examples/input of Sphinx extension.

This should be a folder in the Sphinx source directory, and it should be
configured to be ignored by Sphinx in the ``exclude_patterns`` variable
within ``conf.py``.
"""

SRC_IPYNB_ROOT: Final[Path] = COOKBOOK_DATA_ROOT / "notebook-src"
"""
Path to download notebooks to and cache unmodified notebooks in.

Should be a subdirectory of ``COOKBOOK_DATA_ROOT``.
"""

EXEC_IPYNB_ROOT: Final[Path] = COOKBOOK_DATA_ROOT / "examples"
"""
Path to store executed notebooks in, ready for HTML rendering.

Should be a subdirectory of ``COOKBOOK_DATA_ROOT``.
"""
COLAB_IPYNB_ROOT: Final[Path] = COOKBOOK_DATA_ROOT / "notebook-colab"
"""
Path to store notebooks and their required files for Colab.

Should be a subdirectory of ``COOKBOOK_DATA_ROOT``.
"""

ZIPPED_IPYNB_ROOT: Final[Path] = COOKBOOK_DATA_ROOT / "notebook-zipped"
"""
Path to store zips of notebooks and their required files.

Should be a subdirectory of ``COOKBOOK_DATA_ROOT``.
"""

THUMBNAIL_FILENAME = "thumbnail.png"
"""
Filename for a notebook's thumbnail.

Should be in the same directory as the notebook. If the file does not exist, a
default thumbnail will be used.
"""

REPO_EXAMPLES_DIR = "examples"
"""Directory in source repositories where the examples are stored."""

CACHE_BRANCH = "examples-cache"
"""Branch of the openff-docs repository where cached notebooks are stored."""
