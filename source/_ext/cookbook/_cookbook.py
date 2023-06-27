"""Implementation of the cookbook Sphinx extension"""
from __future__ import annotations

from dataclasses import dataclass
import json
from os import stat
from pathlib import Path
import shutil

from sphinx.application import Sphinx
from sphinx.config import Config

from .github import download_dir
from .notebook import (
    insert_cell,
    get_metadata,
    find_notebooks,
    notebook_zip,
    set_metadata,
)
from .globals import (
    EXEC_IPYNB_ROOT,
    REPO_EXAMPLES_DIR,
    CACHE_BRANCH,
    COLAB_IPYNB_ROOT,
    OPENFF_DOCS_ROOT,
    ZIPPED_IPYNB_ROOT,
    GITHUB_REPOS,
)


def inject_tags_index(notebook: dict) -> dict:
    """Inject an `index` directive containing the notebook's metadata tags"""

    tags = get_metadata(notebook, "tags", ["untagged"])

    return insert_cell(
        notebook,
        cell_type="markdown",
        source=[
            f"```{{index}} {', '.join(tags)}",
            f"```",
        ],
    )


def inject_links(app: Sphinx, notebook: dict, docpath: Path) -> dict:
    user, repo, *path = str(docpath.relative_to(EXEC_IPYNB_ROOT)).split("/")
    path = "/".join(path)

    tag = get_metadata(notebook, "src_repo_tag", "main")

    github_uri = (
        f"https://github.com/{user}/{repo}/blob/{tag}/{REPO_EXAMPLES_DIR}/{path}"
    )

    # TODO: Test colab
    colab_path = COLAB_IPYNB_ROOT.relative_to(OPENFF_DOCS_ROOT) / user / repo / path
    colab_uri = f"https://colab.research.google.com/github/openforcefield/openff-docs/blob/{CACHE_BRANCH}/{colab_path}"

    zip_path = notebook_zip(docpath).relative_to(app.srcdir)

    return insert_cell(
        notebook,
        cell_type="markdown",
        source=[
            f"[Download Notebook](path:/{zip_path})",
            f"[View in GitHub]({github_uri})",
            f"[Open in Google Colab]({colab_uri})",
        ],
    )


def process_notebook(app: Sphinx, docname: str, source: list[str]):
    docpath = Path(app.env.doc2path(docname))
    if docpath.suffix != ".ipynb":
        return

    notebook = json.loads(source[0])

    notebook = inject_links(app, notebook, docpath)
    notebook = inject_tags_index(notebook)

    # Copy the modified NGLView JS to the build directory
    # TODO: Remove this once https://github.com/nglviewer/nglview/pull/1064 gets
    #       into a release
    out_path = Path(app.outdir) / app.env.doc2path(docname, base=False)
    js_src = Path(__file__).parent / "js/nglview-js-widgets.js"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(js_src, out_path.parent)

    # Tell Sphinx we don't expect this notebook to show up in a toctree
    set_metadata(notebook, "orphan", True)

    source[0] = json.dumps(notebook)


def download_cached_notebooks(app: Sphinx, config: Config):
    """
    Download notebooks from the cache iff they do not exist.

    Note that the cache is not checked for changes; if you want to refresh the
    cache, you must manually delete it.
    """
    for directory in [
        COLAB_IPYNB_ROOT,
        EXEC_IPYNB_ROOT,
        ZIPPED_IPYNB_ROOT,
    ]:
        for repo in GITHUB_REPOS:
            repo, _, tag = repo.partition("#")
            repo_directory = directory / repo
            if not repo_directory.exists():
                download_dir(
                    "openforcefield/openff-docs",
                    str(repo_directory.relative_to(OPENFF_DOCS_ROOT)),
                    repo_directory,
                    refspec=CACHE_BRANCH,
                )

    # Exclude notebooks from linkcheck
    config["linkcheck_exclude_documents"].extend(
        str(doc.relative_to(app.srcdir)) for doc in Path(EXEC_IPYNB_ROOT).glob("**/*")
    )


def find_notebook_docnames(app, env, docnames):
    """Find the downloaded notebooks and make sure Sphinx sees them"""
    for path in find_notebooks(EXEC_IPYNB_ROOT):
        docname = env.project.path2doc(str(path))
        docnames.append(docname)
