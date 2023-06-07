"""Code for working with GitHub in both the Sphinx extension and proc_examples.py"""
import shutil
from pathlib import Path
from typing import Generator, Iterable, Literal, Optional, Union

from git.repo import Repo
from git.diff import DiffIndex


class UpdatedNotebooks:
    """Stores paths that must be reprocessed or cleaned up"""

    def __init__(
        self,
        reprocess: Optional[Iterable[Path]] = None,
        cleanup: Optional[Iterable[Path]] = None,
        rebuild_all: Optional[Iterable[str]] = None,
    ):
        # Find the notebooks associated with each change, and remove duplicates
        reprocess = set(self._find_all_notebooks(reprocess))
        cleanup = set(
            notebook for notebook in (cleanup or []) if notebook.suffix == ".ipynb"
        )

        # We don't need to cleanup notebooks we're reprocessing, so remove them
        cleanup = cleanup - reprocess

        self.reprocess = list(reprocess)
        """List of paths to reprocess"""
        self.cleanup = list(cleanup)
        """List of paths to clean up"""
        self.rebuild_all = list(rebuild_all or [])
        """List of the repos that need to be completely rebuilt"""

    @classmethod
    def from_diff(cls, diffs) -> "UpdatedNotebooks":
        reprocess = []
        cleanup = []

        for diff in diffs:
            # Files we need to re-process (from additions, copies, renames,
            # modifications)
            if diff.change_type in "ACRM":
                reprocess.append(Path(diff.b_path))
            # Files we need to clean up (from deletions, renames)
            if diff.change_type == "DR":
                cleanup.append(Path(diff.a_path))

        return cls(reprocess=reprocess, cleanup=cleanup)

    @classmethod
    def new_rebuild_all(cls) -> "UpdatedNotebooks":
        return cls(rebuild_all=True)

    @classmethod
    def _find_all_notebooks(
        cls, paths: Optional[Iterable[Path]]
    ) -> Generator[Path, None, None]:
        """Find the notebooks that could correspond to each file"""
        if paths is None:
            return

        for path in paths:
            yield from cls._find_notebooks(path)

    @staticmethod
    def _find_notebooks(path: Path) -> list[Path]:
        """Find the notebooks that could correspond to a file"""
        if path.suffix == ".ipynb":
            return [path]

        for parent in path.parents:
            notebooks = [*parent.glob("*.ipynb")]
            if notebooks:
                return notebooks
        return []

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(reprocess={list(self.reprocess)},"
            + f" cleanup={list(self.cleanup)}, rebuild_all={self.rebuild_all})"
        )

    def extend(self, other):
        """Merge the elements of ``other`` into ``self``"""
        reprocess = set(self.reprocess + other.reprocess)
        cleanup = set(self.cleanup + other.cleanup) - reprocess
        rebuild_all = set(self.rebuild_all + other.rebuild_all)

        self.reprocess = list(reprocess)
        self.cleanup = list(cleanup)
        self.rebuild_all = list(rebuild_all)


def download_dir(
    src_repo: str,
    src_path: str,
    examples_path: Path,
    refspec: Union[str, None] = None,
) -> UpdatedNotebooks:
    """Download src_path from GitHub src_repo

    The folder is downloaded to to ``<examples_path>/<src_repo>/<src_path>``.
    Git is used to only download new or updated files. The names of
    newly-downloaded or updated files are returned."""
    local_repo_path = examples_path / src_repo

    # Try a simple pull - the repo will have been set up with sparse_checkout
    # already so we don't need to bother with that
    try:
        repo = Repo(local_repo_path)

        previous = repo.head.commit
        repo.git.checkout(refspec)
        new = repo.head.commit
    except Exception:
        # Clean up whatever's there
        if local_repo_path.exists():
            shutil.rmtree(local_repo_path)
    else:
        if previous == new:
            return UpdatedNotebooks()
        else:
            return UpdatedNotebooks.from_diff(previous.diff(new))

    # If the repo doesn't exist, or a pull fails for some other reason, clone
    local_repo_path.mkdir(parents=True, exist_ok=True)
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
    # Just checkout the examples directory
    repo.git.sparse_checkout("set", src_path)
    repo.git.checkout()

    return UpdatedNotebooks(rebuild_all=[src_repo])
