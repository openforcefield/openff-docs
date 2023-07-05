"""Code for working with GitHub in both the Sphinx extension and proc_examples.py"""
import shutil
from pathlib import Path
from typing import Generator, Union
from tempfile import TemporaryDirectory
from importlib import import_module
from os import environ

from git.cmd import Git
from git.repo import Repo
import requests
from packaging.version import Version

from .globals_ import COLAB_IPYNB_ROOT, OPENFF_DOCS_ROOT, CACHE_BRANCH


def download_dir(
    src_repo: str,
    src_path: str,
    dst_path: Path,
    refspec: Union[str, None] = None,
):
    """Download the contents of src_path from GitHub src_repo to dst_path."""
    with TemporaryDirectory() as local_repo_path:
        # Clone metadata of entire history, but no blobs (file data)
        # "--depth=1" is not an optimization, because it prevents us from
        # checking out commits other than HEAD. f"--branch={refspec}" is not an
        # optimization, because it prevents us from checking out commits by hash
        repo = Repo.clone_from(
            url=f"https://github.com/{src_repo}.git",
            to_path=local_repo_path,
            multi_options=[
                "--no-checkout",
                "--filter=blob:none",
            ],
        )
        # Set up sparse checkout of the desired path
        repo.git.sparse_checkout("set", src_path)
        # Checkout (and therefore download) the desired refspec
        repo.git.checkout(refspec)

        # Move the requested directory to dst_path
        shutil.move(Path(local_repo_path) / src_path, dst_path)


def get_repo_tagnames(repo: str) -> Generator[str, None, None]:
    """Get a list of tagnames in a GitHub repository"""
    r = requests.get(
        f"https://api.github.com/repos/{repo}/tags",
        params={"per_page": "100"},
    )
    r.raise_for_status()
    yield from (tag["name"] for tag in r.json())

    while "next" in r.links:
        r = requests.get(r.links["next"]["url"])
        r.raise_for_status()
        yield from (tag["name"] for tag in r.json())


def get_stable_tagname(repo: str) -> str:
    """
    Get the tag name for the release with the greatest semver version number.
    """
    return max(get_repo_tagnames(repo), key=Version)


def get_tag_matching_installed_version(repo: str) -> str:
    """
    Get the tag name for the release that matches the installed version.

    ``repo`` should be a GitHub repository path with an installed module
    matching the repository's name (or following the OpenFF convention). The
    project should provide a version number in a top-level ``__version__: str``
    attribute. The tag must match the version number ± a leading "v".
    """
    # Get the module name for the repo
    org, project = repo.split("/")
    if org == "openforcefield" and project.startswith("openff-"):
        module = "openff." + project[7:]
    else:
        module = project

    # Get the version from the available module
    try:
        version = import_module(module).__version__
    except Exception:
        raise ValueError(f"Error encountered while getting version for repo {repo}")

    # Return the tag corresponding to the version
    tagnames = [*get_repo_tagnames(repo)]
    if version in tagnames:
        return version
    elif f"v{version}" in tagnames:
        return f"v{version}"
    elif version.lower().startswith("v") and version[1:] in tagnames:
        return version[1:]
    else:
        raise ValueError(
            f"Could not find commit hash or tag for version {version}; found tags {tagnames}"
        )
