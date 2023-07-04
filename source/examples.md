# Examples

This page assembles examples drawn from throughout the OpenFF stack. Each example is provided in the form of a notebook; that is, as annotated code blocks alongside their output. You can download the corresponding notebook file and run it yourself either locally or in Google Colab with the links at the top of each page.

## Tutorials

Tutorials describing key workflows from start to finish, with detailed explanations of what's going on.

:::{cookbook}
---
categories: tutorial
---
:::

## Parametrization and Evaluation

Quick examples describing use of OpenFF tools for system prep, parametrization, energy evaluation, and simulation.

:::{cookbook}
---
categories: parametrization_evaluation
---
:::

## Combining Force Fields

Examples combining OpenFF and SMIRNOFF force fields with force fields from other projects.

:::{cookbook}
---
categories: force_field_interop
---
:::

## Force Field Development

Modifying, tweaking, manipulating, inspecting, and re-fitting force fields.

:::{cookbook}
---
categories: force_field_dev
---
:::

## Uncategorized

Notebooks that don't fit in to the above categories.

:::{cookbook}
---
categories: uncategorized, other
---
:::

## Running examples locally

Each example (links above) provides a "Download notebook" link, which downloads a compressed .TGZ archive including the notebook, all the files needed to run it, a [Conda environment specification] YAML file, and a script called `run_notebook.sh`. Extracting the entire file and executing this script will download all the software needed to run the notebook into a virtual environment and then run the notebook:

```shell
./run_notebook.sh
```

For more information, see the comments in the script itself. If you have a Mamba installation already (see [](install)), you can prepare the environment by hand:

```shell
mamba env create --file environment.yaml --name openff-examples
mamba activate openff-examples
jupyter lab *.ipynb
```

[Conda environment specification]: managing_environments
