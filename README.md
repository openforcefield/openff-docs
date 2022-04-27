# openff-docs
Documentation for the Open Force Field ecosystem

Documentation for individual packages live in each project's own repository.
This repo produces a landing page for all OpenFF docs.

Check out the rendered docs at <docs.openforcefield.org>.

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
