from ._cookbook import (
    remove_old_notebooks,
    process_notebook,
    find_notebook_docnames,
    CookbookDirective,
)
from sphinx.application import Sphinx as Application


def setup(app: Application):
    # TODO: Remove these config values and replace with simpler versions
    app.add_config_value(
        "cookbook_default_conda_forge_deps",
        default=[],
        rebuild="env",
    )
    app.add_config_value(
        "cookbook_default_required_files",
        default=None,
        rebuild="env",
    )
    app.add_config_value(
        "cookbook_required_files_base_uri",
        default="",
        rebuild="env",
    )

    app.add_config_value(
        "cookbook_example_repos",
        default=[],
        rebuild="env",
    )
    app.add_config_value(
        "cookbook_examples_path",
        default="_static/examples/",
        rebuild="env",
    )
    app.add_config_value(
        "cookbook_dont_fetch",
        default=False,
        rebuild="env",
    )
    # TODO: Implement this config value
    app.add_config_value(
        "cookbook_ignore_notebook_pattern",
        default=["deprecated/**"],
        rebuild="env",
    )

    app.connect("env-purge-doc", remove_old_notebooks)
    app.connect("source-read", process_notebook)
    app.connect("env-before-read-docs", find_notebook_docnames)
    app.add_directive("cookbook", CookbookDirective)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
