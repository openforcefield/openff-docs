"""Implementation of the cookbook Sphinx extension"""

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

from .notebook import insert_cell, get_metadata, find_notebooks, notebook_zip
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
    if not hasattr(env, "cookbook_notebooks"):
        env.cookbook_notebooks = []  # type: ignore

    for path in find_notebooks(EXEC_IPYNB_ROOT):
        docname = env.project.path2doc(str(path))
        env.cookbook_notebooks.append(docname)
        docnames.append(docname)


class CookbookDirective(TocTree):
    """
    Directive to draw thumbnails of the cookbook.
    """

    has_content = False

    def run(self):
        node = CookbookNode()
        node.extend(super().run())
        toctree = node[0][0]

        toctree["entries"].extend(
            [(None, docname) for docname in self.env.cookbook_notebooks]
        )
        toctree["includefiles"].extend(self.env.cookbook_notebooks)

        return [node]


class CookbookNode(docutils.nodes.Element):
    def __init__(self, *args, **kwargs):
        self.entries = []
        return super().__init__(*args, **kwargs)


def proc_cookbook_toctree(
    app: Application,
    doctree: sphinx.addnodes.document,
    docname: str,
):
    for cookbook_node in doctree.findall(CookbookNode):
        toctree_node = cookbook_node[0][0]
        # print("proc_cookbook_toctree", app, toctree_node, docname)
        for title, notebook in toctree_node["entries"]:
            if title is not None:
                pass
            elif (title := app.env.titles[notebook].astext()) != "<no title>":
                pass
            else:
                title = Path(notebook).stem.replace("_", " ")

            uri = app.builder.get_relative_uri(docname, notebook)

            cookbook_node.entries.append((notebook, title, uri))

        cookbook_node.children = []


def depart_cookbook_html(translator: HTML5Translator, node: CookbookNode):
    translator.body.append("<div class='notebook-grid'>")
    for notebook, notebook_title, notebook_uri in node.entries:
        # TODO: Get the thumbnail from the notebook
        thumbnail_url = "https://openforcefield.org/about/branding/img/openforcefield_v2_full-color.png"
        translator.body.extend(
            [
                f"<a class='notebook-grid-elem' href={notebook_uri}>",
                f"<img src={thumbnail_url}>",
                "<div class='caption'>",
                notebook_title or Path(notebook).stem,
                "</div>",
            ]
        )
        print(notebook, notebook_title, notebook_uri)
    translator.body.append("</div>")


def include_css_files(app: Application, filenames: list[str]):
    srcdir = Path(__file__).parent / "css"

    def copy_custom_css_file(application: Application, exc):
        if application.builder.format == "html" and not exc:
            staticdir = Path(app.builder.outdir) / "_static"
            for filename in filenames:
                copy_asset_file(str(srcdir / filename), str(staticdir))

    app.connect("build-finished", copy_custom_css_file)
    for filename in filenames:
        app.add_css_file(filename)
