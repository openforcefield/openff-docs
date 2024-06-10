# Protein Preparation in Jupyter

Today, Jupyter notebooks are everything you need to prepare a molecular dynamics simulation. Not only do they provide a unified interface to all the tools needed to prepare and visualize a simulation, they also provide an easy way to record, repeat, and even publish your workflow, including any alterations needed for a particularly stubborn system.

This workshop covers the preparation of a protein system from a structure downloaded from the PDB, entirely in the Jupyter notebook, complete with 3D visualizations at every step of the way. We hope to make it accessible even to new MD practitioners, assuming they have some familiarity with Python. 

First session
: [Feb 27 2024 23:00 UTC](https://time.is/1000_28_Feb_2024_in_Canberra/Tokyo/Auckland,_New_Zealand/Los_Angeles/Chicago/Phoenix/New_York/UTC?Protein_Prep_OpenFF_Workshop)

Second Session
: [Apr 17 2024 12:00 UTC](https://time.is/2200_17_Apr_2024_in_Canberra/Beijing/Berlin/Los_Angeles/Chicago/Phoenix/New_York/London/UTC?Protein_Prep_OpenFF_Workshop)

Materials and Google Colab links can be found below.

## Workshop Materials

This workshop is a live demonstration designed to be followed along with on your own computer. The entire workshop can be executed in your browser without installing anything using Google Colab:

[🤝 Protein Prep Workshop at Google Colab](https://colab.research.google.com/github/openforcefield/openff-docs/blob/main/source/workshops/2024/protein_prep/colab-protein_prep.ipynb)

For better performance and to keep any artifacts produced, you can install the relevant software locally and execute the notebook there. This requires an installation of Mamba, Micromamba, or similar conda-forge compatible package manager (see [](/install.md)). First, download the workshop materials:

[2024_protein_prep_workshop_materials.zip](path:protein_prep/2024_protein_prep_workshop_materials.zip)

Extract the zip file and open a terminal in the extracted directory. Then, create the environment:

```shell
mamba env create -n protein_prep_workshop -f env.yml
```

And run Jupyter Lab in the new environment:

```shell
mamba run -n protein_prep_workshop jupyter-lab protein_prep.ipynb
```
