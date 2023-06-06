"""Script to execute and pre-process example notebooks"""

from zipfile import ZIP_DEFLATED, ZipFile
from pathlib import Path
import json
import shutil

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
import yaml

from _notebook import (
    notebook_zip,
    notebook_colab,
    get_metadata,
    insert_cell,
    find_notebooks,
    is_bare_notebook,
)
from _github import download_dir
from _globals import *


def needed_files(notebook_path: Path) -> list[tuple[Path, Path]]:
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
            + f"\nName the intended Conda environment {PACKAGED_ENV_NAME}."
        )

    return list(files.items())


def create_zip(notebook_path: Path):
    """
    Create a zip file with all needed files from a jupyter notebook path
    """
    zip_path = notebook_zip(notebook_path)
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(
        file=zip_path,
        mode="w",
        compression=ZIP_DEFLATED,
        compresslevel=9,
    ) as zip_file:
        for path, arcname in needed_files(notebook_path):
            zip_file.write(path, arcname=arcname)


def create_colab_notebook(
    src: Path,
):
    """
    Create a copy of the notebook at src for Google Colab and save it to dst.
    """
    with open(src) as file:
        notebook = json.load(file)

    # Add a cell that installs the notebook's dependencies
    notebook = insert_cell(
        notebook,
        cell_type="code",
        source=[
            "# Execute this cell to make this notebook's dependencies available",
            "!pip install -q condacolab",
            "import condacolab",
            "condacolab.install_mambaforge()",
            f"!mamba env update -q -n base -f {PACKAGED_ENV_NAME}",
        ],
    )

    dst = notebook_colab(src)
    dst.parent.mkdir(parents=True, exist_ok=True)

    for path, rel_path in needed_files(src):
        shutil.copy(path, dst.parent / rel_path)

    # Make sure the environment file doesn't include a name, as this seems to
    # break condacolab
    with open(dst.parent / PACKAGED_ENV_NAME, "r+") as env_file:
        env_yaml = yaml.safe_load(env_file)
        if "name" in env_yaml:
            del env_yaml["name"]
            env_file.seek(0)
            yaml.dump(env_yaml, env_file)
            env_file.truncate()

    with open(dst, "w") as file:
        json.dump(notebook, file)


def execute_notebook(src: Path):
    """Execute a notebook and retain its widget state"""
    with open(src, "r") as f:
        nb = nbformat.read(f, nbformat.NO_CONVERT)

    # Embed any thumbnail.png by displaying it in an injected hidden cell
    # marked as the thumbnail.
    # https://nbsphinx.readthedocs.io/en/latest/hidden-cells.html
    # https://nbsphinx.readthedocs.io/en/latest/gallery/cell-tag.html
    # TODO: See if this works
    if Path.exists(src.parent / "thumbnail.png"):
        insert_cell(
            nb,
            source=["display(thumbnail.png)"],
            metadata={"nbsphinx": "hidden", "tags": ["nbsphinx-thumbnail"]},
        )

    executor = ExecutePreprocessor(timeout=600, store_widget_state=True)
    executor.preprocess(nb, {"metadata": {"path": src.parent}})

    dst = EXEC_IPYNB_ROOT / src.relative_to(SRC_IPYNB_ROOT)
    dst.parent.mkdir(parents=True, exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)


def main(do_proc=True, do_exec=True):
    print("Working in", Path().resolve())

    for repo in GITHUB_REPOS:
        print("Downloading", repo, "to", (SRC_IPYNB_ROOT / repo).resolve())
        download_dir(repo, "examples", SRC_IPYNB_ROOT)

    notebooks = [*find_notebooks(SRC_IPYNB_ROOT)]

    if do_proc:
        for notebook in notebooks:
            # TODO: Check if the notebook has changed since the last time we ran this
            print("Processing", notebook)
            create_colab_notebook(notebook)
            create_zip(notebook)

    if do_exec:
        for notebook in notebooks:
            print(
                "Executing ",
                notebook.relative_to(SRC_IPYNB_ROOT),
                end="...",
                sep="",
                flush=True,
            )
            execute_notebook(notebook)
            print(" done.")


if __name__ == "__main__":
    import sys

    main(
        do_proc=not "--skip-proc" in sys.argv,
        do_exec=not "--skip-exec" in sys.argv,
    )
