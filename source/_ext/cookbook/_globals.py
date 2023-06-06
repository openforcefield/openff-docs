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
UNIVERSAL_ENV_PATH: Final = (
    Path(__file__) / "../../../../devtools/conda-envs/examples_env.yml"
).resolve()
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
# TODO: Get latest release, not `main`
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
]
"""Directory names to not descend into when searching for notebooks."""

SRC_IPYNB_ROOT: Final[Path] = Path("src")
"""Path to download notebooks to and cache unmodified notebooks in"""
EXEC_IPYNB_ROOT: Final[Path] = Path("exec")
"""Path to store executed notebooks in, ready for HTML rendering"""
COLAB_IPYNB_ROOT: Final[Path] = Path("colab")
"""Path to store notebooks and their required files for Colab"""
ZIPPED_IPYNB_ROOT: Final[Path] = Path("zipped")
"""Path to store zips of notebooks and their required files"""
