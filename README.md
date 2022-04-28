# openff-docs
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
