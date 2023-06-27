from sphinx.application import Sphinx

from ._cookbook import (
    process_notebook,
    find_notebook_docnames,
    download_cached_notebooks,
)

from ._gallery import (
    CookbookDirective,
    CookbookNode,
    CookbookEntryNode,
    proc_cookbook_toctree,
)


def do_nothing(self, node):
    pass


def setup(app: Sphinx):
    app.connect("config-inited", download_cached_notebooks)
    app.connect("env-before-read-docs", find_notebook_docnames)
    app.connect("source-read", process_notebook)
    app.connect("doctree-resolved", proc_cookbook_toctree)
    app.add_directive("cookbook", CookbookDirective)

    app.add_node(
        CookbookNode,
        html=(CookbookNode.visit, CookbookNode.depart),
        latex=(do_nothing, do_nothing),
        text=(do_nothing, do_nothing),
    )
    app.add_node(
        CookbookEntryNode,
        html=(CookbookEntryNode.visit, CookbookEntryNode.depart),
        latex=(do_nothing, do_nothing),
        text=(do_nothing, do_nothing),
    )

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
