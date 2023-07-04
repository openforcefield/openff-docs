from multiprocessing import Value
from pathlib import Path

from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective
import sphinx.addnodes
import docutils.nodes
from sphinx.writers.html5 import HTML5Translator
from docutils.parsers.rst.directives import choice
from sphinx.application import Sphinx

from ._cookbook import find_notebooks
from .globals import EXEC_IPYNB_ROOT
from .utils import flatten


class CookbookDirective(SphinxDirective):
    """
    Directive to draw thumbnails of the cookbook.

    The "categories" option specifies the categories of notebooks that should be
    included in this cookbook. It is a comma-separated string listing category
    names. Omitting this option will include all categories. The
    names "uncategorized" and "other" are special; "uncategorized" is applied
    to any notebook without a category, whereas "other" will include all
    categories not rendered in a cookbook somewhere else on the same page as
    the current directive (possibly including "uncategorized").
    """

    optional_arguments = 1
    option_spec = {
        "categories": lambda x: [
            s.strip().lower().replace("-", "_") for s in str(x).split(",")
        ],
    }
    has_content = False

    def run(self):
        node = CookbookNode(categories=self.options.get("categories", []))

        for path in find_notebooks(EXEC_IPYNB_ROOT):
            entry = CookbookEntryNode.from_path(self.env, path)
            node.append(entry)

        return [node]


class CookbookNode(docutils.nodes.Element):
    """Docutils node representing the cookbook directive"""

    def __init__(
        self,
        categories: list[str] | None = None,
        *args,
        **kwargs,
    ):
        self.categories: list[str] = categories if categories else []
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
        source_repo: str | None = None,
        thumbnail_uri: str | None = None,
        *args,
        **kwargs,
    ):
        self.docname: str = docname
        """The docname of the notebook."""
        self.source_repo: str | None = source_repo
        """The GitHub repository the notebook was sourced from."""
        self.uri: str | None = None
        """URI of the built notebook."""
        self.title: str | None = None
        """Title of the notebook."""

        super().__init__(*args, **kwargs)

        self.extend(
            [
                docutils.nodes.image(
                    "",
                    uri="https://openforcefield.org/about/branding/img/openforcefield_v2_full-color.png"
                    if thumbnail_uri is None
                    else thumbnail_uri,
                    alt="",
                    candidates={"?": ""},
                    classes=["output", "image_png"],
                )
            ]
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
        else:
            thumbnail_uri = None

        _, source_repo, *_ = str(path.relative_to(EXEC_IPYNB_ROOT)).split("/")

        return cls(
            docname=docname, source_repo=source_repo, thumbnail_uri=thumbnail_uri
        )

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
        badges = []
        if "/experimental/" in node.docname:
            badges.append(("experimental", "red"))
        if node.source_repo:
            badges.append((node.source_repo, "#00bc4e"))

        translator.body.extend(
            [
                "<div class='caption'>",
                node.title,
                "</div>",
                "<div class='badges'>",
                *(
                    f"<span class='badge' style='color:{color};'>{badge}</span>"
                    for badge, color in badges
                ),
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

    cookbook_nodes = [*doctree.findall(CookbookNode)]

    # Get the categories that are in a cookbook directive on this page
    categories_on_page = {*flatten(node.categories for node in cookbook_nodes)}

    for cookbook_node in cookbook_nodes:
        cookbook_categories = cookbook_node.categories

        if cookbook_categories:
            # "uncategorised" is a special category for notebooks whose metadata
            # doesn't specify a category
            cookbook_entries_with_categories = (
                (entry, metadata[entry.docname].get("category", "uncategorized"))
                for entry in cookbook_node.children
            )
            # "other" is a special category for cookbook directives that should
            # include all notebooks not rendered in any other category on the
            # current page.
            # TODO: Make this all notebooks not rendered in the entire project?
            cookbook_node.children = [
                entry
                for entry, entry_category in cookbook_entries_with_categories
                if entry_category in cookbook_categories
                or (
                    "other" in cookbook_categories
                    and entry_category not in categories_on_page
                )
            ]

        for entry in cookbook_node.children:
            entry.title = app.env.titles[entry.docname].astext()
            if entry.title == "<no title>":
                entry.title = Path(entry.docname).stem.replace("_", " ")

            entry.uri = app.builder.get_relative_uri(docname, entry.docname)
