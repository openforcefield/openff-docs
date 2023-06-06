"""Code for working with GitHub in both the Sphinx extension and proc_examples.py"""
import shutil
from pathlib import Path
from typing import Literal

from git.repo import Repo


def download_dir(
    src_repo: str, src_path: str, examples_path: Path
) -> dict[Literal["new", "updated", "removed"], Path]:
    """Download src_path from GitHub src_repo

    The folder is downloaded to to ``<examples_path>/<src_repo>/<src_path>``.
    Git is used to only download new or updated files. The names of
    newly-downloaded or updated files are returned."""
    local_repo_path = examples_path / src_repo

    # Try a simple pull
    try:
        repo = Repo(local_repo_path)
        repo.remotes.origin.pull(depth=1)
        return
    except Exception:
        # Clean up whatever's there
        if local_repo_path.exists():
            shutil.rmtree(local_repo_path)

    # If the repo doesn't exist, or a pull fails for some other reason, clone
    local_repo_path.mkdir(parents=True, exist_ok=True)
    # Clone without downloading anything
    repo = Repo.clone_from(
        url=f"https://github.com/{src_repo}.git",
        to_path=local_repo_path,
        multi_options=[
            "--depth=1",
            "--filter=tree:0",
            "--no-checkout",
        ],
    )
    # Just checkout the examples directory
    repo.git.sparse_checkout("set", src_path)
    repo.git.checkout()
    # TODO: Clean up and report removed files
