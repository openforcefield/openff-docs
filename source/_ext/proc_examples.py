"""Script to execute and pre-process example notebooks"""

import re
from typing import Tuple, List, Final
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path
import json
import shutil
from multiprocessing import Pool
from time import sleep
import sys
import tarfile
from functools import partial
import traceback

import nbformat
from nbconvert.preprocessors.execute import ExecutePreprocessor
import yaml
from git.repo import Repo


sys.path.append(str(Path(__file__).parent))

from cookbook.notebook import (
    notebook_download,
    notebook_colab,
    get_metadata,
    insert_cell,
    find_notebooks,
    is_bare_notebook,
    set_metadata,
)
from cookbook.github import download_dir, get_tag_matching_installed_version
from cookbook.globals_ import *
from cookbook.utils import set_env, to_result, in_regexes


class NotebookExceptionError(ValueError):
    def __init__(self, src: str, exc: Exception):
        self.src: str = str(src)
        self.exc: Exception = exc
        self.tb: str = "".join(traceback.format_exception(exc, chain=False))


def needed_files(notebook_path: Path) -> List[Tuple[Path, Path]]:
    """
    Get the files needed to run the notebook

    Returns a list of 2-tuples of paths. The first path in each tuple is the
    path to the existing file, the second is where the file should go relative
    to the notebook directory.

    If ``notebook_path`` is a bare notebook
    (see :func:`_notebook.is_bare_notebook`), the returned list begins with
    only the notebook itself. Otherwise, it begins with all the files from
    inside ``notebook_path.parent``, except for any with names in
    ``IGNORED_FILES``.  The list is guaranteed to include a file with the name
    given by ``PACKAGED_ENV_NAME``. This is a Conda-environment from within the
    ``notebook_path``, or if there are no Conda environments it is the
    environment specified by ``UNIVERSAL_ENV_PATH``.
    """
    if is_bare_notebook(notebook_path):
        src_paths = [notebook_path]
    else:
        src_paths = [
            path
            for path in notebook_path.parent.iterdir()
            if path.name not in IGNORED_FILES
        ]

    # Get the relative and absolute paths, except if its a file we don't want
    files: dict[Path, Path] = {
        path: path.relative_to(notebook_path.parent) for path in src_paths
    }
    # Detect any already-included candidate environment files
    environment_files = [
        path
        for path in src_paths
        if Path(path.name)
        in (
            PACKAGED_ENV_NAME.with_suffix(".yaml"),
            PACKAGED_ENV_NAME.with_suffix(".yml"),
        )
    ]
    # Make sure an environment file is included and named correctly
    if len(environment_files) == 0:
        # If no environment file is included, include the universal one
        files[UNIVERSAL_ENV_PATH] = PACKAGED_ENV_NAME
    elif len(environment_files) == 1:
        # If exactly one environment file is already included, make sure it has
        # the correct name
        files[environment_files[0]] = PACKAGED_ENV_NAME
    elif PACKAGED_ENV_NAME in environment_files:
        # If multiple environment files are included and one of them has the
        # right name, do nothing
        # This is unnecessary now as there are only two acceptable file names,
        # but this'll save us a bug if that list ever expands
        pass
    else:
        raise ValueError(
            f"Could not choose a Conda environment file from multiple candidates:"
            + "".join("\n  " + str(path) for path in environment_files)
            + f"\nName the intended Conda environment '{PACKAGED_ENV_NAME}'."
        )

    return list(files.items())


def create_download(notebook_path: Path):
    """
    Create a tgz file with all needed files from a jupyter notebook path
    """
    tgz_path = notebook_download(notebook_path)
    tgz_path.parent.mkdir(parents=True, exist_ok=True)

    with tarfile.open(
        name=tgz_path,
        mode="w:gz",
    ) as tgz_file:
        for path, arcname in needed_files(notebook_path):
            tgz_file.add(path, arcname=arcname)

        # Also include the run_notebook.sh script
        path = Path(__file__).parent / "run_notebook.sh"
        tgz_file.add(path, arcname=path.name)


def create_colab_notebook(src: Path, cache_branch: str):
    """
    Create a copy of the notebook at src for Google Colab and save it to dst.
    """
    with open(src) as file:
        notebook = json.load(file)

    files = needed_files(src)

    # Decide where we're going to write this modified notebook
    dst = notebook_colab(src)
    dst.parent.mkdir(parents=True, exist_ok=True)

    # Copy over all the files Colab will need
    for path, rel_path in files:
        if path.is_dir():
            shutil.copytree(path, dst.parent / rel_path)
        else:
            shutil.copy2(path, dst.parent / rel_path)

    # Get the base URI to download files from the cache
    base_uri = (
        f"https://raw.githubusercontent.com/openforcefield/openff-docs/{cache_branch}"
    )

    # Get a list of the wget commands we'll need to download the files
    wget_files = [
        f"!wget -q {base_uri}/{dst.parent.relative_to(OPENFF_DOCS_ROOT)}/{relative_path}"
        for _, relative_path in files
        if relative_path.suffix != ".ipynb"
    ]

    # Add a cell that installs the notebook's dependencies
    notebook = insert_cell(
        notebook,
        cell_type="code",
        source=[
            "# Execute this cell to make this notebook's dependencies available",
            "!pip install -q condacolab",
            "import condacolab",
            "condacolab.install()",
            *wget_files,
            f"!mamba env update -q --name=base --file={PACKAGED_ENV_NAME}",
            "from google.colab import output",
            "output.enable_custom_widget_manager()",
        ],
    )

    # Make sure the environment file doesn't include a name, as this seems to
    # break condacolab
    with open(dst.parent / PACKAGED_ENV_NAME, "r+") as env_file:
        env_yaml = yaml.safe_load(env_file)
        if "name" in env_yaml:
            del env_yaml["name"]
            env_file.seek(0)
            yaml.dump(env_yaml, env_file)
            env_file.truncate()

    # Write the file
    with open(dst, "w") as file:
        json.dump(notebook, file)


def execute_notebook(
    src_and_tag: Tuple[Path, str],
    cache_branch: str,
):
    """Execute a notebook and retain its widget state"""
    # Unpack the argument
    src, tag = src_and_tag

    # Get the source
    src_rel = src.relative_to(SRC_IPYNB_ROOT)
    print("Executing", src_rel)

    with open(src, "r") as f:
        nb = nbformat.read(f, nbformat.NO_CONVERT)

    # TODO: See if we can convince this to do each notebook single-threaded?
    with set_env(
        OPENMM_CPU_THREADS="1",
    ):
        executor = ExecutePreprocessor(
            kernel_name="python3",
            timeout=1200,
        )
        executor.store_widget_state = True
        # Execute the notebook
        # TODO: Run in the notebook-specific Conda environment?
        try:
            executor.preprocess(nb, {"metadata": {"path": src.parent}})
        except Exception as e:
            print("Failed to execute", src.relative_to(SRC_IPYNB_ROOT))
            raise NotebookExceptionError(str(src_rel), e)

    # Store the tag used to execute the notebook in metadata
    set_metadata(nb, "src_repo_tag", tag)

    # Store the branch where this notebook will be saved in metadata
    set_metadata(nb, "cookbook_cache_branch", cache_branch)

    # Write the executed notebook
    dst = EXEC_IPYNB_ROOT / src_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)

    # Copy the thumbnail
    thumbnail_path = src.with_name(THUMBNAIL_FILENAME)
    if thumbnail_path.is_file():
        shutil.copy(
            thumbnail_path,
            EXEC_IPYNB_ROOT / thumbnail_path.relative_to(SRC_IPYNB_ROOT),
        )

    print("Successfully executed", src.relative_to(SRC_IPYNB_ROOT))


def delay_iterator(iterator, seconds=1.0):
    """Introduce a delay to iteration.

    This may be helpful to avoid race conditions with process pools."""
    for item in iterator:
        yield item
        sleep(seconds)


def clean_up_notebook(notebook: Path):
    """
    Delete processed versions of the notebook.

    Note that this does not delete the source notebook.
    """
    notebook_download(notebook).unlink()
    shutil.rmtree(notebook_colab(notebook).parent)
    exec_notebook = EXEC_IPYNB_ROOT / notebook.relative_to(SRC_IPYNB_ROOT)
    exec_notebook.unlink()


def main(
    cache_branch: str,
    do_proc=True,
    do_exec=True,
    prefix: Path | None = None,
    processes: int | None = None,
    failed_notebooks_log: Path | None = None,
    allow_failures: bool = False,
):
    print("Working in", Path().resolve())

    notebooks: List[Tuple[Path, str]] = []
    # Download the examples from latest releases on GitHub
    shutil.rmtree(SRC_IPYNB_ROOT, ignore_errors=True)
    for repo in GITHUB_REPOS:
        repo, _, tag = repo.partition("#")

        dst_path = SRC_IPYNB_ROOT / repo
        tag = tag or get_tag_matching_installed_version(repo)

        print(f"Downloading {repo}#{tag} to {dst_path.resolve()}")

        download_dir(
            repo,
            REPO_EXAMPLES_DIR,
            dst_path,
            refspec=tag,
        )

        # Find the notebooks we need to process
        notebooks.extend(
            (notebook, tag)
            for notebook in find_notebooks(dst_path)
            if str(notebook.relative_to(SRC_IPYNB_ROOT)) not in SKIP_NOTEBOOKS
        )

    # Create Colab and downloadable versions of the notebooks
    if do_proc:
        shutil.rmtree(COLAB_IPYNB_ROOT, ignore_errors=True)
        shutil.rmtree(DOWNLOAD_IPYNB_ROOT, ignore_errors=True)
        for notebook, _ in notebooks:
            print("Processing", notebook)
            create_colab_notebook(notebook, cache_branch)
            create_download(notebook)

    # Execute notebooks in parallel for rendering as HTML
    execution_failed = False
    if do_exec:
        shutil.rmtree(EXEC_IPYNB_ROOT, ignore_errors=True)
        # Context manager ensures the pool is correctly terminated if there's
        # an exception
        with Pool(processes=processes) as pool:
            # Wait a second between launching subprocesses
            # Workaround https://github.com/jupyter/nbconvert/issues/1066
            exec_results = [
                *pool.imap(
                    to_result(
                        partial(execute_notebook, cache_branch=cache_branch),
                        NotebookExceptionError,
                    ),
                    delay_iterator(notebooks),
                )
            ]

        exceptions: list[NotebookExceptionError] = [
            result for result in exec_results if isinstance(result, Exception)
        ]
        ignored_exceptions = [
            exc for exc in exceptions if in_regexes(exc.src, OPTIONAL_NOTEBOOKS)
        ]

        if exceptions:
            for exception in exceptions:
                print(
                    "-" * 80
                    + "\n"
                    + f"{exception.src} failed. Traceback:\n\n{exception.tb}"
                )
                if not in_regexes(exception.src, OPTIONAL_NOTEBOOKS):
                    execution_failed = True
            print(f"The following {len(exceptions)}/{len(notebooks)} notebooks failed:")
            for exception in exceptions:
                print("    ", exception.src)
            print("For tracebacks, see above.")

        if failed_notebooks_log is not None:
            print(f"Writing log to {failed_notebooks_log.absolute()}")
            failed_notebooks_log.write_text(
                json.dumps(
                    {
                        "n_successful": len(notebooks) - len(exceptions),
                        "n_total": len(notebooks),
                        "n_ignored": len(ignored_exceptions),
                        "failed": [
                            exc.src
                            for exc in exceptions
                            if exc not in ignored_exceptions
                        ],
                        "ignored": [exc.src for exc in ignored_exceptions],
                    }
                )
            )

    if isinstance(prefix, Path):
        prefix.mkdir(parents=True, exist_ok=True)

        for directory in [
            COLAB_IPYNB_ROOT,
            EXEC_IPYNB_ROOT,
            DOWNLOAD_IPYNB_ROOT,
            SRC_IPYNB_ROOT,
        ]:
            shutil.move(
                directory,
                prefix / directory.relative_to(OPENFF_DOCS_ROOT),
            )

    if execution_failed:
        exit(1)


if __name__ == "__main__":
    import sys, os

    # TODO: Implement special handling for experimental notebooks?
    # Set the INTERCHANGE_EXPERIMENTAL environment variable
    # It kinda makes sense to do this here - it means users can see our
    # experimental stuff without being bothered by it, but if they want to *use*
    # it they hit a road bump.
    os.environ["INTERCHANGE_EXPERIMENTAL"] = "1"

    # --prefix is the path to store the output in
    prefix = None
    for arg in sys.argv:
        if arg.startswith("--prefix="):
            prefix = Path(arg[9:])
    if "--prefix" in sys.argv:
        raise ValueError("Specify prefix in a single argument: `--prefix=<prefix>`")

    # --processes is the number of processes to multitask notebook execution over
    processes = None
    for arg in sys.argv:
        if arg.startswith("--processes="):
            processes = int(arg[12:])
    if "--processes" in sys.argv:
        raise ValueError(
            "Specify processes in a single argument: `--processes=<processes>`"
        )

    cache_branch = DEFAULT_CACHE_BRANCH
    for arg in sys.argv:
        if arg.startswith("--cache-branch="):
            cache_branch = arg[15:]
    if "--cache-branch" in sys.argv:
        raise ValueError(
            "Specify cache branch in a single argument: `--cache-branch=<branch>`"
        )

    # --log-failures is the path to store a list of failing notebooks in
    failed_notebooks_log = None
    for arg in sys.argv:
        if arg.startswith("--log-failures="):
            failed_notebooks_log = Path(arg[15:])
    if "--log-failures" in sys.argv:
        raise ValueError(
            "Specify path to log file in a single argument: `--log-failures=<path>`"
        )

    # if --allow-failures is True, do not exit with error code 1 if a
    # notebook fails
    allow_failures = "false"
    for arg in sys.argv:
        if arg.startswith("--allow-failures="):
            allow_failures = arg[17:].lower()
    if allow_failures in ["true", "1", "y", "yes", "t"]:
        allow_failures = True
    elif allow_failures in ["false", "0", "n", "no", "false"]:
        allow_failures = False
    else:
        raise ValueError(
            f"Didn't understand value of --allow-failures {allow_failures}; try `true` or `false`"
        )
    if "--log-failures" in sys.argv:
        raise ValueError(
            "Specify value in a single argument: `--allow-failures=true` or `--allow-failures=false`"
        )

    main(
        cache_branch=cache_branch,
        do_proc=not "--skip-proc" in sys.argv,
        do_exec=not "--skip-exec" in sys.argv,
        prefix=prefix,
        processes=processes,
        failed_notebooks_log=failed_notebooks_log,
        allow_failures=allow_failures,
    )
