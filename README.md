# openff-docs

 [![Read the Docs](https://img.shields.io/readthedocs/openff-docs?style=for-the-badge&label=Website%20Build)](https://readthedocs.org/projects/openff-docs/builds/)

Documentation for the Open Force Field ecosystem

Documentation for individual packages live in each project's own repository.
This repo produces a landing page for all OpenFF docs.

Check out the rendered docs at [docs.openforcefield.org].

## Building the docs

Clone the repo:

```shell
git clone https://github.com/openforcefield/openff-docs.git
cd openff-docs
```

Make a Conda environment with [Mamba](https://github.com/mamba-org/mamba):

```shell
mamba env create --name openff-docs --file devtools/conda-envs/rtd_env.yml
```

Activate the environment and build the docs:

```shell
conda activate openff-docs
sphinx-build -b html -j auto source build/html
```

### The examples page

The examples page relies on a cache of pre-processed examples collected from other repositories, as well as a Sphinx extension. This pre-processing includes steps like injecting a setup cell for Google Colab, executing the notebooks that are presented in Sphinx, and preparing .TGZ archives of each notebook with its required files. The cache is stored in git branches in this repository so that it can be accessed from Google Colab. The Sphinx extension is coded in `source/_ext/cookbook`, and shares some code with the pre-processing script `source/_ext/proc_examples.py`.

When a Sphinx build starts, the cookbook Sphinx extension will look in the file system for the cache files. If it doesn't find them, it will get the cache from the branch specified in `cookbook.globals_.DEFAULT_CACHE_BRANCH`. To generate the cache files locally, run the `proc_examples.py` script from the `devtools/conda-envs/examples_env.yml` environment. This environment includes dependencies for both the examples themselves and the pre-processing code:

```shell
mamba env create --file devtools/conda-envs/examples_env.yml --name openff-docs-examples
mamba activate openff-docs-examples
python source/_ext/proc_examples.py
```

This involves executing all the notebooks - it takes about half an hour on GitHub actions, but can execute notebooks in parallel so may be much faster where more cores are available.

#### Adding a new repo

To collect examples from a new project, add the project to the `devtools/conda-envs/examples_env.yml` environment, add the GitHub repository identifier (eg, "openforcefield/openff-toolkit") to the `GITHUB_REPOS` list in `source/_ext/cookbook/globals_.py`, and regenerate the cache.

`proc_examples.py` will look for a Git tag that matches the version number found in the top-level `__version__` attribute. It will work with an exact match, or else plus or minus a leading "v" relative to the `__version__` string. The module name is inferred from the repository name in `GITHUB_REPOS`; for instance, for `openforcefield/openff-toolkit`, the `openff.toolkit.__version__` attribute is checked.

If looking for a tag fails, a particular tag, branch, or commit may be specified in `GITHUB_REPOS` by appending a hash sign and the reference name:

```python
GITHUB_REPOS = [
    "openforcefield/openff-toolkit#0.14.0",
    ...
]
```

Note that while the example notebooks will be taken from this commit, they will be executed in the examples environment, so its important to make sure the same version is installed there.

#### Regenerating the cache in GitHub

The cache for the `main` branch, which is served at <https://docs.openforcefield.org>, is automatically regenerated every night at midnight UTC, and also when a new commit is merged into `main`. To manually regenerate it, dispatch the [`cookbook_preproc.yaml` workflow](https://github.com/openforcefield/openff-docs/actions/workflows/cookbook_preproc.yaml) from the `main` branch with the `PR#` input left blank. ReadTheDocs will automatically rebuild when the `main` branch cache is successfully regenerated via this workflow.

Caches for PRs are stored in their own branches. To regenerate the cache for a PR, create a comment on the PR consisting only of the text:

```
/regenerate-cache
```

Note that you must have push permissions on this repository for this command to work. Note also that in a PR, the RTD build must be manually restarted after the cache is finished generating. The github-actions bot will comment on the PR to tell you when regeneration starts and finishes.

#### Preparing examples for openff-docs

Generally, any Jupyter notebook (extension `.ipynb`) in a subfolder of the `examples` directory in any repository in `GITHUB_REPOS` should be automatically included without modification, but there are some things you can do to improve the quality of your example:

- Include exactly one top-level heading as a title. The first top-level heading in each notebook is used as that notebook's title; it should be clear from that title what the notebook does even outside the context of the source repository. Avoid using multiple top-level headings, as it disturbs the natural hierarchy of the documentation.
- Add a category. A Jupyter notebook is a JSON file with a top-level object (`dict` in Python terms). That object has a `"metadata"` property which specifies arbitrary metadata for the notebook. Adding an entry like `"category": "force_field_dev"` to the metadata object will place the notebook in the matching category on the examples page. See `source/examples.md` for the available categories.
- Add a thumbnail. A file named `thumbnail.png` in the same folder as the notebook will be used as the thumbnail for that notebook in the examples page.
- Avoid `nglview.show_file(...)`; use `nglview.show_structure_file(...)` instead. The former loads the file with JavaScript and does not work in embedded contexts like the examples page; the latter loads the file with Python and then passes its contents to JavaScript and so does work.

Note that changes to examples must generally be in a release before they are rendered in the examples page; but see [Adding a new repo](#adding-a-new-repo) for advice on overriding this.

## Linking to new projects

ReadTheDocs should be configured to provide [redirects] that allow subprojects to be found at URLs like [docs.openforcefield.org/toolkit]. Redirects can be defined in the [Redirects tab] of the Admin page at [readthedocs.org]. For each project, two "exact" redirects should be defined:

1. From `/projectname/$rest` to the URL of the project's docs. This handles arbitrary links within the docs.
2. From `/projectname` to the URL of the project's docs. This handles the bare project name without a trailing forward slash.

For projects hosted outside of ReadTheDocs, the "to" URL should be the URL of the hosted documentation:

> Redirect type: `Exact redirect` \
> From URL: `/standards/$rest` \
> To URL: `https://openforcefield.github.io/standards/`

> Redirect type: `Exact redirect` \
> From URL: `/standards` \
> To URL: `https://openforcefield.github.io/standards/`


For projects hosted within ReadTheDocs, the project should be [added as a subproject] of `openff-docs` and the "to" URL should be `/projects/projectname`

> Child: `openff-interchange` \
> Alias: `interchange`

> Redirect type: `Exact redirect` \
> From URL: `/interchange/$rest` \
> To URL: `/projects/interchange/`

> Redirect type: `Exact redirect` \
> From URL: `/interchange` \
> To URL: `/projects/interchange/`:

You must have maintainer access to a project on RTD to add it as a subproject. If a project cannot be added as a subproject, the "to" URL can be set to the URL of the hosted documentation as with projects hosted externally.

[docs.openforcefield.org]: https://docs.openforcefield.org/
[redirects]: https://docs.readthedocs.io/page/user-defined-redirects.html
[docs.openforcefield.org/toolkit]: https://docs.openforcefield.org/toolkit/
[readthedocs.org]: https://readthedocs.org/
[Redirects tab]: https://readthedocs.org/dashboard/openff-docs/redirects/
[added as a subproject]: https://readthedocs.org/dashboard/openff-docs/subprojects/
