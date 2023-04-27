import json
from pathlib import Path
from typing import Generator, List, Optional, Any, Tuple, TypeVar
from uuid import uuid4
from copy import deepcopy
import shutil
from tempfile import TemporaryDirectory

from sphinx.application import Sphinx as Application
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from docutils import nodes
from sphinx import addnodes
from sphinx.directives.other import TocTree
from sphinx.util.docutils import SphinxDirective
from git.repo import Repo
from nbsphinx import NbGallery


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
    default,
):
    """Get a notebook's metadata value for a key, or the given default if the key is absent"""
    return notebook.get("metadata", {}).get(key, default)


# TODO: Make sure this works
# TODO: Use examples conda environments instead of a list of packages
# TODO: Make a version of this for Binder
def create_colab_notebook(notebook, notebook_path: Path, outpath: Path, config: Config):
    """Create a copy of the notebook for Google Colab and save it to output

    The copy will have a cell inserted at the start of the notebook that gathers
    the notebook's dependencies. These dependencies come in two sorts:
     - Conda dependencies, installed via mambaforge
     - Files, downloaded from the config value `cookbook_required_files_base_uri`

    These dependencies can be specified in the following places. The first value found
    in the following order is used:
    1. In the `conda_forge_dependencies` or `required_files` metadata fields for an
       individual notebook
    2. In the `cookbook_default_conda_forge_deps` or `cookbook_default_required_files`
       config values for the entire cookbook
    3. (files only) If the `cookbook_default_required_files` config value is not set,
       all files in the notebook's directory except those with the `.ipynb` file extension
       will be used as dependencies. Set `cookbook_default_required_files` to the empty
       list to specify no dependencies as a default.

    """

    if config.cookbook_default_required_files is None:
        file_list = [
            fn for fn in notebook_path.parent.glob("*.*") if fn.suffix != ".ipynb"
        ]
    else:
        file_list = list(config.cookbook_default_required_files)

    file_deps = get_metadata(
        notebook,
        "required_files",
        file_list,
    )

    conda_deps = get_metadata(
        notebook,
        "conda_forge_dependencies",
        list(config.cookbook_default_conda_forge_deps),
    )

    if file_deps:
        wgets = [
            "# We also need to get a few files that the cookbook depends on",
            *(
                f"!wget -q '{config.cookbook_required_files_base_uri}/{dep}'"
                for dep in file_deps
            ),
        ]
    else:
        wgets = []

    notebook = insert_cell(
        notebook,
        cell_type="code",
        source=[
            "# Execute this cell to install OpenMM in the Colab environment",
            "!pip install -q condacolab",
            "import condacolab",
            "condacolab.install_mambaforge()",
            f"!mamba install {' '.join(conda_deps)}",
            *wgets,
        ],
    )

    outpath = outpath.absolute()
    outpath.parent.mkdir(parents=True, exist_ok=True)
    with outpath.open("w") as file:
        json.dump(notebook, file)


def inject_tags_index(notebook: dict) -> dict:
    """Inject an `index` directive containing the notebook's metadata tags"""

    tags = get_metadata(notebook, "tags", ["untagged"])

    return insert_cell(
        notebook,
        cell_type="raw",
        metadata={"raw_mimetype": "text/restructuredtext"},
        source=[
            f".. index:: {', '.join(tags)}",
        ],
    )


def inject_links(notebook: dict, docpath: Path, cookbook_examples_path: Path) -> dict:
    user, repo, *path = str(docpath.relative_to(cookbook_examples_path)).split("/")
    path = "/".join(path)

    github_url = f"https://github.com/{user}/{repo}/blob/main/{path}"
    # TODO: Figure out how to get the conda colab install cell into this
    colab_url = (
        f"https://colab.research.google.com/github/{user}/{repo}/blob/main/{path}"
    )

    return insert_cell(
        notebook,
        cell_type="raw",
        metadata={"raw_mimetype": "text/restructuredtext"},
        source=[
            f":download:`Download Notebook </{docpath}>`",
            f"`View in GitHub <{github_url}>`_",
            f"`Open in Google Colab <{colab_url}>`_",
        ],
    )


def process_notebook(app: Application, docname: str, source: list[str]):
    build_colab = Path(app.outdir) / "colab"

    docpath = Path(app.env.doc2path(docname, False))

    if docpath.suffix == ".ipynb":
        notebook = json.loads(source[0])
        create_colab_notebook(notebook, docpath, build_colab / docpath, app.config)

        notebook = inject_links(notebook, docpath, app.config.cookbook_examples_path)
        notebook = inject_tags_index(notebook)

        source[0] = json.dumps(notebook)


def remove_colab_notebook(app: Application, env: BuildEnvironment, docname: str):
    """Remove generated colab notebooks that are no longer needed"""
    outdir = Path(app.outdir)
    colab_path = outdir / "colab" / docname
    colab_path = colab_path.with_suffix(".ipynb")
    # We check is_relative_to just in case docname is absolute
    if colab_path.exists() and colab_path.is_relative_to(outdir / "colab"):
        colab_path.unlink()


def download_dir(src_repo: str, src_path: str, examples_path: Path):
    """Download src_path from GitHub src_repo

    The folder is downloaded to to ``<examples_path>/<src_repo>/<src_path>``"""
    local_repo_path = examples_path / src_repo

    # Try a simple pull
    try:
        repo = Repo(local_repo_path)
        repo.remotes.origin.pull(depth=1)
        return
    except Exception as e:
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


def collect_notebooks(app: Application, config: Config):
    """Download examples directories from example repositories"""
    app.cookbook_examples_path = Path(app.srcdir) / config.cookbook_examples_path  # type: ignore
    if config.cookbook_dont_fetch:
        return
    for repo in config.cookbook_example_repos:
        print("Collecting examples from", repo)

        download_dir(repo, "examples", app.cookbook_examples_path)  # type: ignore


def find_notebooks(path: Path) -> Generator[Path, None, None]:
    """Descend through a file tree and yield all the notebooks inside"""
    index = [*path.iterdir()]
    while index:
        item = index.pop(0)

        if item.is_dir():
            index.extend([subitem for subitem in item.iterdir()])
        else:
            if item.suffix.lower() == ".ipynb":
                yield path / item


def find_notebook_docnames(app, env, docnames):
    """Find the downloaded notebooks and make sure Sphinx sees them"""
    if not hasattr(app, "cookbook_notebooks"):
        app.cookbook_notebooks = []  # type: ignore

    for repo in env.config.cookbook_example_repos:
        for path in find_notebooks(app.cookbook_examples_path / repo / "examples"):
            docname = env.project.path2doc(str(path.relative_to(app.srcdir)))
            app.cookbook_notebooks.append(docname)
            docnames.append(docname)


class CookbookDirective(NbGallery):
    """
    Directive to draw thumbnails of the cookbook.
    """

    def run(self):
        nodes = super().run()
        toctree = nodes[0][0][0]

        toctree["entries"].extend(
            [(None, docname) for docname in self.env.app.cookbook_notebooks]
        )
        toctree["includefiles"].extend(self.env.app.cookbook_notebooks)

        return nodes


def setup(app: Application):
    # TODO: Remove these config values and replace with simpler versions
    app.add_config_value(
        "cookbook_default_conda_forge_deps",
        default=[],
        rebuild="env",
    )
    app.add_config_value(
        "cookbook_default_required_files",
        default=None,
        rebuild="env",
    )
    app.add_config_value(
        "cookbook_required_files_base_uri",
        default="",
        rebuild="env",
    )

    # Everything after this can stay :)
    app.add_config_value(
        "cookbook_example_repos",
        default=[],
        rebuild="env",
    )
    app.add_config_value(
        "cookbook_examples_path",
        default="_static/examples/",
        rebuild="env",
    )
    app.add_config_value(
        "cookbook_dont_fetch",
        default=False,
        rebuild="env",
    )
    # TODO: Implement this config value
    app.add_config_value(
        "cookbook_ignore_notebook_pattern",
        default=["deprecated/**"],
        rebuild="env",
    )

    app.connect("config-inited", collect_notebooks)
    app.connect("env-purge-doc", remove_colab_notebook)
    app.connect("source-read", process_notebook)
    app.connect("env-before-read-docs", find_notebook_docnames)
    app.add_directive("cookbook", CookbookDirective)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
