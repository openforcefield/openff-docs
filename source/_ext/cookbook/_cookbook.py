"""Implementation of the cookbook Sphinx extension"""
from __future__ import annotations

import json
from pathlib import Path

from sphinx.application import Sphinx
from sphinx.config import Config

from .github import download_dir
from .notebook import (
    insert_cell,
    get_metadata,
    find_notebooks,
    notebook_download,
    set_metadata,
)
from .globals_ import (
    EXEC_IPYNB_ROOT,
    REPO_EXAMPLES_DIR,
    DEFAULT_CACHE_BRANCH,
    COLAB_IPYNB_ROOT,
    OPENFF_DOCS_ROOT,
    DOWNLOAD_IPYNB_ROOT,
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
    cache_branch = get_metadata(notebook, "cookbook_cache_branch", DEFAULT_CACHE_BRANCH)

    github_uri = (
        f"https://github.com/{user}/{repo}/blob/{tag}/{REPO_EXAMPLES_DIR}/{path}"
    )
    zip_path = notebook_download(docpath).relative_to(app.srcdir)

    colab_path = COLAB_IPYNB_ROOT.relative_to(OPENFF_DOCS_ROOT) / user / repo / path
    colab_uri = (
        "https://colab.research.google.com/github/openforcefield/openff-docs/blob"
    )
    colab_uri = colab_uri + f"/{cache_branch}/{colab_path}"

    return insert_cell(
        notebook,
        cell_type="markdown",
        source=[
            f"{{ .notebook-links }}",
            f"[Download Notebook](path:/{zip_path}){{ .button }}",
            f"[View in GitHub]({github_uri}){{ .button }}",
            f"[Open in Google Colab]({colab_uri}){{ .button }}",
        ],
    )


def inject_experimental_warning(notebook: dict) -> dict:
    return insert_cell(
        notebook,
        cell_type="markdown",
        source=[
            "```{admonition} Experimental",
            "This notebook is experimental. It may use private or unstable",
            "APIs, break suddenly, or produce scientifically unsound results.",
            "```",
        ],
    )


def process_notebook(app: Sphinx, docname: str, source: list[str]):
    docpath = Path(app.env.doc2path(docname))
    if docpath.suffix != ".ipynb":
        return

    notebook = json.loads(source[0])

    notebook = inject_links(app, notebook, docpath)
    notebook = inject_tags_index(notebook)

    if "/experimental/" in docname:
        notebook = inject_experimental_warning(notebook)

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
        DOWNLOAD_IPYNB_ROOT,
    ]:
        for repo in GITHUB_REPOS:
            repo, _, tag = repo.partition("#")
            repo_directory = directory / repo
            if not repo_directory.exists():
                download_dir(
                    "openforcefield/openff-docs",
                    str("main" / repo_directory.relative_to(OPENFF_DOCS_ROOT)),
                    repo_directory,
                    refspec=DEFAULT_CACHE_BRANCH,
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
