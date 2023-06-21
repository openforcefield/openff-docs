"""Implementation of the cookbook Sphinx extension"""
from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import shutil

from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective
from sphinx.util.fileutil import copy_asset_file
from sphinx.directives.other import TocTree
import sphinx.addnodes
import docutils.nodes
import docutils.parsers.rst.directives
from sphinx.writers.html5 import HTML5Translator

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
    SRC_IPYNB_ROOT,
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


def remove_old_notebooks(app: Sphinx, env: BuildEnvironment, docname: str):
    """Clean up processed notebooks from outdir"""
    # outdir = Path(app.outdir)
    # colab_path = outdir / "colab" / docname
    # colab_path = colab_path.with_suffix(".ipynb")
    # # We check is_relative_to just in case docname is absolute
    # if colab_path.exists() and colab_path.is_relative_to(outdir / "colab"):
    #     colab_path.unlink()


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
            repo_directory = directory / repo
            if not repo_directory.exists():
                download_dir(
                    "openforcefield/openff-docs",
                    str(repo_directory.relative_to(OPENFF_DOCS_ROOT)),
                    repo_directory,
                    refspec=CACHE_BRANCH,
                )


def find_notebook_docnames(app, env, docnames):
    """Find the downloaded notebooks and make sure Sphinx sees them"""
    for path in find_notebooks(EXEC_IPYNB_ROOT):
        docname = env.project.path2doc(str(path))
        docnames.append(docname)


@dataclass
class CookbookEntry:
    path: Path
    """The absolute path to the notebook."""
    docname: str
    """The docname of the notebook."""
    uri: str | None = None
    """URI of the built notebook."""
    title: str | None = None
    """Title of the notebook."""
    # TODO: Set this to the actual path of the thumbnail if it exists
    thumbnail_uri: str = (
        "https://openforcefield.org/about/branding/img/openforcefield_v2_full-color.png"
    )
    """URI of the notebook's thumbnail for the gallery."""

    @classmethod
    def from_path(cls, env: BuildEnvironment, path: Path) -> CookbookEntry:
        docname = env.path2doc(str(path))

        if docname is None:
            raise ValueError(
                "path is not a document in this Sphinx environment.",
            )

        return CookbookEntry(path, docname)


class CookbookDirective(SphinxDirective):
    """
    Directive to draw thumbnails of the cookbook.
    """

    has_content = False

    def run(self):
        node = CookbookNode()

        for path in find_notebooks(EXEC_IPYNB_ROOT):
            entry = CookbookEntry.from_path(self.env, path)
            node.entries.append(entry)

        return [node]


class CookbookNode(docutils.nodes.Element):
    """Docutils node representing the cookbook directive"""

    def __init__(self, *args, **kwargs):
        self.entries: list[CookbookEntry] = []
        return super().__init__(*args, **kwargs)


def proc_cookbook_toctree(
    app: Sphinx,
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
        translator.body.extend(
            [
                f"<a class='notebook-grid-elem' href={entry.uri}>",
                f"<img src={entry.thumbnail_uri}>",
                "<div class='caption'>",
                entry.title,
                "</div>",
            ]
        )
    translator.body.append("</div>")


def include_css_files(app: Sphinx):
    """Include all the CSS files in the `cookbook/css` directory"""
    srcdir = Path(__file__).parent / "css"

    filenames = [str(fn) for fn in srcdir.glob("**/*.css")]

    def copy_custom_css_file(application: Sphinx, exc):
        if application.builder.format == "html" and not exc:
            staticdir = Path(app.builder.outdir) / "_static"
            for filename in filenames:
                copy_asset_file(filename, str(staticdir))

    app.connect("build-finished", copy_custom_css_file)
    for filename in filenames:
        app.add_css_file(filename)
