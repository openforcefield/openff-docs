"""Script to execute and pre-process example notebooks"""
from typing import Tuple, List, Final
from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path
import json
import shutil
from multiprocessing import Pool
from time import sleep
import sys
import tarfile

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


def create_colab_notebook(src: Path, cache_uri_prefix: str | None = None):
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
        shutil.copy(path, dst.parent / rel_path)

    # Get the base URI to download files from the cache
    base_uri = (
        f"https://raw.githubusercontent.com/openforcefield/openff-docs/{CACHE_BRANCH}"
    )
    if cache_uri_prefix is not None:
        base_uri = base_uri + "/" + cache_uri_prefix

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
            "condacolab.install_mambaforge()",
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


def execute_notebook(src_and_tag: Tuple[Path, str]):
    """Execute a notebook and retain its widget state"""
    # Unpack the argument
    src, tag = src_and_tag

    # Get the source
    src_rel = src.relative_to(SRC_IPYNB_ROOT)
    print("Executing", src_rel)

    with open(src, "r") as f:
        nb = nbformat.read(f, nbformat.NO_CONVERT)

    # TODO: See if we can convince this to do each notebook single-threaded?
    executor = ExecutePreprocessor(
        kernel_name="python3",
        timeout=600,
    )
    executor.store_widget_state = True
    # Execute the notebook
    # TODO: Run in the notebook-specific Conda environment?
    try:
        executor.preprocess(nb, {"metadata": {"path": src.parent}})
    except Exception as e:
        raise ValueError(f"Exception encountered while executing {src_rel}")

    # Store the tag used to execute the notebook in metadata
    set_metadata(nb, "src_repo_tag", tag)

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

    print("Done executing", src.relative_to(SRC_IPYNB_ROOT))


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
    do_proc=True,
    do_exec=True,
    prefix: Path | None = None,
    cache_prefix: str | None = None,
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
        notebooks.extend((notebook, tag) for notebook in find_notebooks(dst_path))

    # Create Colab and downloadable versions of the notebooks
    if do_proc:
        shutil.rmtree(COLAB_IPYNB_ROOT, ignore_errors=True)
        shutil.rmtree(DOWNLOAD_IPYNB_ROOT, ignore_errors=True)
        for notebook, _ in notebooks:
            print("Processing", notebook)
            create_colab_notebook(notebook, cache_prefix)
            create_download(notebook)

    # Execute notebooks in parallel for rendering as HTML
    if do_exec:
        shutil.rmtree(EXEC_IPYNB_ROOT, ignore_errors=True)
        # Context manager ensures the pool is correctly terminated if there's
        # an exception
        with Pool() as pool:
            # Wait a second between launching subprocesses
            # Workaround https://github.com/jupyter/nbconvert/issues/1066
            _ = [*pool.imap_unordered(execute_notebook, delay_iterator(notebooks))]

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

    # --cache-prefix is the path that the output will be stored in within the cache
    cache_prefix = None
    for arg in sys.argv:
        if arg.startswith("--cache-prefix="):
            cache_prefix = arg[15:]
    if "--prefix" in sys.argv:
        raise ValueError(
            "Specify Colab prefix in a single argument: `--cache-prefix=<prefix>`"
        )

    main(
        do_proc=not "--skip-proc" in sys.argv,
        do_exec=not "--skip-exec" in sys.argv,
        prefix=prefix,
        cache_prefix=cache_prefix,
    )
