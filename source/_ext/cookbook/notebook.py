"""Code for working with notebooks in both the Sphinx extension and proc_examples.py"""
from typing import Any, List, Optional, Generator
from uuid import uuid4
from copy import deepcopy
from pathlib import Path
from hashlib import sha1

from .globals_ import (
    EXEC_IPYNB_ROOT,
    DOWNLOAD_IPYNB_ROOT,
    COLAB_IPYNB_ROOT,
    DO_NOT_SEARCH,
    SRC_IPYNB_ROOT,
)


def insert_cell(
    notebook: dict,
    cell_type: str = "code",
    position: int = 0,
    source: Optional[List[str]] = None,
    metadata: Optional[dict] = None,
    outputs: Optional[List[str]] = None,
) -> dict:
    """Insert a cell created from the arguments into a new copy of the notebook

    Args:
        notebook: An ipython/jupyter notebook in dict form. Can be generated
                  by parsing the notebook file as json
        cell_type: The cell type; "code", "markdown", "raw", etc
        position: The position of the new cell in the finished notebook. See dict.insert()
        source: A list of lines of source code for the cell. Newlines are inserted at the
                end of each line in the list
        metadata: A dictionary of metadata values. Should be encodable as json.
        output: A list of lines of text output for the cell. Newlines are inserted at the
                end of each line in the list

    Returns:
        dict: A copy of the input notebook with the cell inserted.
    """
    source = [] if source is None else "\n".join(source).splitlines(keepends=True)
    outputs = [] if outputs is None else "\n".join(outputs).splitlines(keepends=True)
    metadata = {} if metadata is None else metadata
    notebook = deepcopy(notebook)

    cell = {
        "cell_type": cell_type,
        "execution_count": 0,
        "id": str(uuid4()),
        "metadata": metadata,
        "outputs": outputs,
        "source": source,
    }

    notebook.setdefault("cells", []).insert(position, cell)
    return notebook


def get_metadata(
    notebook: dict,
    key: str,
    default: Any,
):
    """Get a notebook's metadata value for a key, or the given default if the key is absent"""
    return notebook.get("metadata", {}).get(key, default)


def set_metadata(notebook: dict, key: str, value: Any):
    """Set a notebook's metadata value for a given key"""
    metadata = notebook.setdefault("metadata", {})
    metadata[key] = value


def is_bare_notebook(docpath: Path) -> bool:
    return docpath.parent.name in ["examples", "experimental", "deprecated"]


def notebook_download(docpath: Path) -> Path:
    """Get the name of the zip file for the notebook at ``docpath``"""
    # Strip off any leading SRC_IPYNB_ROOT or EXEC_IPYNB_ROOT
    if str(docpath).startswith(str(SRC_IPYNB_ROOT) + "/"):
        docpath = Path(str(docpath)[len(str(SRC_IPYNB_ROOT)) + 1 :])
    if str(docpath).startswith(str(EXEC_IPYNB_ROOT) + "/"):
        docpath = Path(str(docpath)[len(str(EXEC_IPYNB_ROOT)) + 1 :])
    # Get the zip file path
    if is_bare_notebook(docpath):
        # Notebook has no needed files, just zip the notebook itself
        return DOWNLOAD_IPYNB_ROOT / docpath.with_suffix(".tgz")
    else:
        # Zip the entire containing folder
        return DOWNLOAD_IPYNB_ROOT / docpath.parent.with_suffix(".tgz")


def notebook_colab(docpath: Path) -> Path:
    """
    Get the path to the Colab notebook for the notebook at ``docpath``.

    The notebook's directory is ``notebook_colab(...).parent``
    """
    # Strip off any leading SRC_IPYNB_ROOT or EXEC_IPYNB_ROOT
    if str(docpath).startswith(str(SRC_IPYNB_ROOT) + "/"):
        docpath = Path(str(docpath)[len(str(SRC_IPYNB_ROOT)) + 1 :])
    if str(docpath).startswith(str(EXEC_IPYNB_ROOT) + "/"):
        docpath = Path(str(docpath)[len(str(EXEC_IPYNB_ROOT)) + 1 :])
    # Get the path to the source notebook
    src_notebook = SRC_IPYNB_ROOT / docpath
    # Get the colab notebook path
    if is_bare_notebook(src_notebook):
        # Put the bare notebook in its own folder, named with the hash of the
        # notebook to avoid collisions
        new_folder = (
            docpath.stem + "_" + sha1(src_notebook.read_bytes()).hexdigest()[:6]
        )
        return COLAB_IPYNB_ROOT / docpath.parent / new_folder / docpath.name
    else:
        # Just use the existing folder
        return COLAB_IPYNB_ROOT / docpath


def find_notebooks(path: Path) -> Generator[Path, None, None]:
    """Descend through a file tree and yield all the notebooks inside"""
    index = [*path.iterdir()]
    while index:
        item = index.pop(0)

        if item.is_dir() and item.name not in DO_NOT_SEARCH:
            index.extend([subitem for subitem in item.iterdir()])
        else:
            if item.suffix.lower() == ".ipynb":
                yield item
