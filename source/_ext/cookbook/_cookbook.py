"""Implementation of the cookbook Sphinx extension"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

from sphinx.application import Sphinx as Application
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective
from sphinx.util.fileutil import copy_asset_file
from sphinx.directives.other import TocTree
import sphinx.addnodes
import docutils.nodes
import docutils.parsers.rst.directives
from sphinx.writers.html5 import HTML5Translator

from .notebook import (
    insert_cell,
    get_metadata,
    find_notebooks,
    notebook_zip,
    set_metadata,
)
from .globals import EXEC_IPYNB_ROOT


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


def inject_links(app: Application, notebook: dict, docpath: Path) -> dict:
    user, repo, *path = str(docpath.relative_to(EXEC_IPYNB_ROOT)).split("/")
    path = "/".join(path)

    github_url = f"https://github.com/{user}/{repo}/blob/main/{path}"
    # TODO: Figure out how to get the conda colab install cell into this
    colab_url = (
        f"https://colab.research.google.com/github/{user}/{repo}/blob/main/{path}"
    )
    zip_path = notebook_zip(docpath).relative_to(app.srcdir)

    return insert_cell(
        notebook,
        cell_type="raw",
        metadata={"raw_mimetype": "text/restructuredtext"},
        source=[
            f":download:`Download Notebook </{zip_path}>`",
            f"`View in GitHub <{github_url}>`_",
            f"`Open in Google Colab <{colab_url}>`_",
        ],
    )


def process_notebook(app: Application, docname: str, source: list[str]):
    docpath = Path(app.env.doc2path(docname))
    if docpath.suffix != ".ipynb":
        return

    notebook = json.loads(source[0])

    notebook = inject_links(app, notebook, docpath)
    notebook = inject_tags_index(notebook)

    # Tell Sphinx we don't expect this notebook to show up in a toctree
    set_metadata(notebook, "orphan", True)

    source[0] = json.dumps(notebook)


def remove_old_notebooks(app: Application, env: BuildEnvironment, docname: str):
    """Clean up processed notebooks from outdir"""
    # outdir = Path(app.outdir)
    # colab_path = outdir / "colab" / docname
    # colab_path = colab_path.with_suffix(".ipynb")
    # # We check is_relative_to just in case docname is absolute
    # if colab_path.exists() and colab_path.is_relative_to(outdir / "colab"):
    #     colab_path.unlink()


def find_notebook_docnames(app, env, docnames):
    """Find the downloaded notebooks and make sure Sphinx sees them"""
    for path in find_notebooks(EXEC_IPYNB_ROOT):
        docname = env.project.path2doc(str(path))
        docnames.append(docname)


@dataclass
class CookbookEntry:
    docname: str
    uri: str | None = None
    title: str | None = None

    @classmethod
    def from_path(cls, env: BuildEnvironment, path: Path) -> CookbookEntry:
        docname = env.path2doc(str(path))

        if docname is None:
            raise ValueError(
                "path is not a document in this Sphinx environment.",
            )

        return CookbookEntry(docname)


class CookbookDirective(SphinxDirective):
    """
    Directive to draw thumbnails of the cookbook.
    """

    has_content = False

    def run(self):
        node = CookbookNode()

        for path in find_notebooks(EXEC_IPYNB_ROOT):
            node.entries.append(CookbookEntry.from_path(self.env, path))

        return [node]


class CookbookNode(docutils.nodes.Element):
    """Docutils node representing the cookbook directive"""

    def __init__(self, *args, **kwargs):
        self.entries: list[CookbookEntry] = []
        return super().__init__(*args, **kwargs)


def proc_cookbook_toctree(
    app: Application,
    doctree: sphinx.addnodes.document,
    docname: str,
):
    """Update the cookbook with URIs and titles"""
    for cookbook_node in doctree.findall(CookbookNode):
        for entry in cookbook_node.entries:
            entry.title = app.env.titles[entry.docname].astext()
            if entry.title == "<no title>":
                entry.title = Path(entry.docname).stem.replace("_", " ")

            entry.uri = app.builder.get_relative_uri(docname, entry.docname)


def depart_cookbook_html(translator: HTML5Translator, node: CookbookNode):
    """Render the CookbookNode in HTML"""
    translator.body.append("<div class='notebook-grid'>")
    for entry in node.entries:
        # TODO: Get the thumbnail from the notebook
        thumbnail_url = "https://openforcefield.org/about/branding/img/openforcefield_v2_full-color.png"
        translator.body.extend(
            [
                f"<a class='notebook-grid-elem' href={entry.uri}>",
                f"<img src={thumbnail_url}>",
                "<div class='caption'>",
                entry.title,
                "</div>",
            ]
        )
    translator.body.append("</div>")


def include_css_files(app: Application):
    """Include all the CSS files in the `cookbook/css` directory"""
    srcdir = Path(__file__).parent / "css"

    filenames = [str(fn) for fn in srcdir.iterdir() if fn.suffix == ".css"]

    def copy_custom_css_file(application: Application, exc):
        if application.builder.format == "html" and not exc:
            staticdir = Path(app.builder.outdir) / "_static"
            for filename in filenames:
                copy_asset_file(filename, str(staticdir))

    app.connect("build-finished", copy_custom_css_file)
    for filename in filenames:
        app.add_css_file(filename)
