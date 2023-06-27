from pathlib import Path

from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective
import sphinx.addnodes
import docutils.nodes
from sphinx.writers.html5 import HTML5Translator
from docutils.parsers.rst.directives import choice
from sphinx.application import Sphinx

from ._cookbook import find_notebooks
from .globals import EXEC_IPYNB_ROOT, CATEGORIES


class CookbookDirective(SphinxDirective):
    """
    Directive to draw thumbnails of the cookbook.
    """

    optional_arguments = 1
    option_spec = {
        "category": lambda x: choice(x, [*CATEGORIES, "uncategorized"]),
    }
    has_content = False

    def run(self):
        node = CookbookNode(category=self.options.get("category", None))

        for path in find_notebooks(EXEC_IPYNB_ROOT):
            entry = CookbookEntryNode.from_path(self.env, path)
            node.append(entry)

        return [node]


class CookbookNode(docutils.nodes.Element):
    """Docutils node representing the cookbook directive"""

    def __init__(
        self,
        category: str | None = None,
        *args,
        **kwargs,
    ):
        self.category = category
        self.children: list[CookbookEntryNode]
        return super().__init__(*args, **kwargs)

    @staticmethod
    def visit(translator: HTML5Translator, node: "CookbookNode"):
        """Render the CookbookNode in HTML"""
        translator.body.append("<div class='notebook-grid'>")

    @staticmethod
    def depart(translator: HTML5Translator, node: "CookbookNode"):
        """Render the CookbookNode in HTML"""
        translator.body.append("</div>")


class CookbookEntryNode(docutils.nodes.Element):
    def __init__(
        self,
        docname: str,
        thumbnail_uri: str = "https://openforcefield.org/about/branding/img/openforcefield_v2_full-color.png",
        *args,
        **kwargs,
    ):
        """The absolute path to the notebook."""
        self.docname: str = docname
        """The docname of the notebook."""
        self.uri: str | None = None
        """URI of the built notebook."""
        self.title: str | None = None
        """Title of the notebook."""

        super().__init__(*args, **kwargs)

        self.append(
            docutils.nodes.image(
                "",
                uri=thumbnail_uri,
                alt="",
                candidates={"?": ""},
                classes=["output", "image_png"],
            )
        )

    @classmethod
    def from_path(cls, env: BuildEnvironment, path: Path) -> "CookbookEntryNode":
        docname = env.path2doc(str(path))

        if docname is None:
            raise ValueError(
                f"path {path} is not a document in this Sphinx environment.",
            )

        if path.with_name("thumbnail.png").is_file():
            thumbnail_uri = str(path.with_name("thumbnail.png").relative_to(env.srcdir))
            return cls(docname=docname, thumbnail_uri=thumbnail_uri)

        return cls(docname=docname)

    @staticmethod
    def visit(translator: HTML5Translator, node: CookbookNode):
        """Render the CookbookEntryNode in HTML"""
        translator.body.extend(
            [
                f"<a class='notebook-grid-elem' href={node.uri}>",
            ]
        )

    @staticmethod
    def depart(translator: HTML5Translator, node: CookbookNode):
        """Render the CookbookEntryNode in HTML"""
        translator.body.extend(
            [
                "<div class='caption'>",
                node.title,
                "</div>",
                "</a>",
            ]
        )


def proc_cookbook_toctree(
    app: Sphinx,
    doctree: sphinx.addnodes.document,
    docname: str,
):
    """Update the cookbook with URIs and titles"""
    metadata = app.env.metadata

    for cookbook_node in doctree.findall(CookbookNode):
        cookbook_category = cookbook_node.category

        if cookbook_category is not None:
            cookbook_node.children = [
                entry
                for entry in cookbook_node.children
                if metadata[entry.docname].get("category", "uncategorized")
                == cookbook_category
            ]

        for entry in cookbook_node.children:
            entry.title = app.env.titles[entry.docname].astext()
            if entry.title == "<no title>":
                entry.title = Path(entry.docname).stem.replace("_", " ")

            entry.uri = app.builder.get_relative_uri(docname, entry.docname)
