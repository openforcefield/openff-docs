"""Implementation of the cookbook Sphinx extension"""

import json
from pathlib import Path
from typing import Generator

from sphinx.application import Sphinx as Application
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from nbsphinx import NbGallery

from ._notebook import insert_cell, get_metadata, find_notebooks, notebook_zip
from ._github import download_dir


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
            f":download:`Download Notebook </{notebook_zip(docpath)}>`",
            f"`View in GitHub <{github_url}>`_",
            f"`Open in Google Colab <{colab_url}>`_",
        ],
    )


def process_notebook(app: Application, docname: str, source: list[str]):
    docpath = Path(app.env.doc2path(docname, False))
    if docpath.suffix != ".ipynb":
        return

    notebook = json.loads(source[0])

    notebook = inject_links(notebook, docpath, app.config.cookbook_examples_path)
    notebook = inject_tags_index(notebook)

    source[0] = json.dumps(notebook)


def remove_old_notebooks(app: Application, env: BuildEnvironment, docname: str):
    """Clean up processed notebooks from outdir"""
    # outdir = Path(app.outdir)
    # colab_path = outdir / "colab" / docname
    # colab_path = colab_path.with_suffix(".ipynb")
    # # We check is_relative_to just in case docname is absolute
    # if colab_path.exists() and colab_path.is_relative_to(outdir / "colab"):
    #     colab_path.unlink()


def collect_notebooks(app: Application, config: Config):
    """Download examples directories from example repositories"""
    app.cookbook_examples_path = Path(app.srcdir) / config.cookbook_examples_path  # type: ignore
    if config.cookbook_dont_fetch:
        return
    for repo in config.cookbook_example_repos:
        print("Collecting examples from", repo)

        download_dir(repo, "examples", app.cookbook_examples_path)  # type: ignore


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
