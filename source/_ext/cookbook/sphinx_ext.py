from sphinx.application import Sphinx

from ._cookbook import (
    remove_old_notebooks,
    process_notebook,
    find_notebook_docnames,
    CookbookDirective,
    include_css_files,
    CookbookNode,
    depart_cookbook_html,
    proc_cookbook_toctree,
)


def do_nothing(self, node):
    pass


def setup(app: Sphinx):
    app.connect("env-before-read-docs", find_notebook_docnames)
    app.connect("env-purge-doc", remove_old_notebooks)
    app.connect("source-read", process_notebook)
    app.connect("doctree-resolved", proc_cookbook_toctree)
    app.add_directive("cookbook", CookbookDirective)
    include_css_files(app)

    app.add_node(
        CookbookNode,
        html=(do_nothing, depart_cookbook_html),
        latex=(do_nothing, do_nothing),
        text=(do_nothing, do_nothing),
    )

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
