"""Code for working with GitHub in both the Sphinx extension and proc_examples.py"""

import shutil
from pathlib import Path
from typing import Generator, Union
from tempfile import TemporaryDirectory
from importlib import import_module

from git.repo import Repo
import requests
from packaging.version import Version

from .utils import next_or_none


def download_dir(
    src_repo: str,
    src_path: str,
    dst_path: Path,
    refspec: Union[str, None] = None,
):
    """Download the contents of src_path from GitHub src_repo to dst_path."""
    with TemporaryDirectory() as local_repo_path:
        # Clone without downloading anything
        repo = Repo.clone_from(
            url=f"https://github.com/{src_repo}.git",
            to_path=local_repo_path,
            multi_options=[
                "--depth=1",
                "--sparse",
                "--no-checkout",
                f"--branch={refspec}",
            ],
        )
        # Just checkout the requested directory
        repo.git.sparse_checkout("set", src_path)
        repo.git.checkout()

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


def tagname_matches_version(tagname: str, version: str) -> bool:
    """
    Check whether the tagname corresponds to the version number.

    Tagnames must match versions exactly, except for the leading `"v"` or `"V"`,
    which may be omitted in either.
    """
    return (
        tagname == version
        or "v" + tagname == version
        or "V" + tagname == version
        or tagname == "v" + version
        or tagname == "V" + version
    )


def get_tag_matching_installed_version(repo: str) -> str:
    """
    Get the tag name for the release that matches the installed version.

    If multiple tag names are found, an arbitrary one is returned.
    """
    # Get the module name for the repo
    org, project = repo.split("/")
    if org == "openforcefield" and project.startswith("openff-"):
        module = "openff." + project[7:]
    else:
        module = project

    # Get the version from the available module
    try:
        version = str(import_module(module).__version__)
    except Exception:
        raise ValueError(f"Error encountered while getting version for repo {repo}")

    # Find a matching tag
    tagnames = [*get_repo_tagnames(repo)]
    if version in tagnames:
        matching_tag = version
    else:
        matching_tag = next_or_none(
            filter(
                lambda tag: tagname_matches_version(tag, version),
                tagnames,
            )
        )

    if matching_tag is None:
        raise ValueError(
            f"Could not find tag for version {version} of repo {repo}; found tags {tagnames}"
        )
    return matching_tag
