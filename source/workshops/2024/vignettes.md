# Things to make and do with OpenFF tools

The OpenFF software ecosystem is a flexible and highly programmable collection of tools that is easy to interface with both cheminformatics suites and MD engines. At the same time, it is oriented towards detecting and rejecting molecular systems that don't make chemical sense, or that are ambiguous in the chemistry they represent. This makes it quite powerful and pleasant to use for a wide range of biomolecular simulation tasks.

This workshop will display this flexibility by demonstrating a variety of unusual uses of the OpenFF ecosystem and its software neighbors. These "vignettes" will run the gamut from useful to cute, robust to experimental, and simple to complex. Rather than focus on the details of how each is accomplished, vignettes will each be demonstrated quickly alongside a brief highlight of the relevant part of the ecosystem. In the hands-on session after the prepared material, participants will be encouraged to investigate a thorny problem of their own with developer support.

First session
: [Mar 12 22:00 UTC](https://time.is/0900_13_Mar_2024_in_Canberra/Tokyo/Auckland,_New_Zealand/Los_Angeles/Chicago/Phoenix/New_York/UTC?OpenFF_Vignettes_Workshop)

: [💨 Join on Zoom](https://us06web.zoom.us/j/88273328068?pwd=VtDJg1lJYbnLAI8aA2VPtYQEaw5Ebj.1)

Second session
: [Apr 24 12:00 UTC](https://time.is/2200_24_Apr_2024_in_Canberra/Beijing/Berlin/Los_Angeles/Chicago/Phoenix/New_York/London/UTC?Vignettes_OpenFF_Workshop)

Zoom links will be published here 24 hours before the sessions begin.

## Workshop Materials

This workshop is a live demonstration designed to be followed along with on your own computer. The entire workshop can be executed in your browser without installing anything using Google Colab:

[🤝 Vignettes Workshop at Google Colab](https://colab.research.google.com/github/openforcefield/openff-docs/blob/main/source/workshops/2024/vignettes/colab-vignettes.ipynb)

For better performance and to keep any artifacts produced, you can install the relevant software locally and execute the notebook there. This requires an installation of Mamba, Micromamba, or similar conda-forge compatible package manager (see [](/install.md)). First, download the workshop materials:

[2024_vignettes_workshop_materials.zip](path:vignettes/2024_vignettes_workshop_materials.zip)

Extract the zip file and open a terminal in the extracted directory. Then, create the environment:

```shell
mamba env create -n vignettes-workshop -f examples_env.yml
```

And run Jupyter Lab in the new environment:

```shell
mamba run -n vignettes-workshop jupyter lab
```
