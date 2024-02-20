# SMIRNOFF Force Fields and You

SMIRNOFF is an open format for specifying molecular mechanics force fields directly for the chemistry of a target molecule, rather than indirectly through abstractions like atom types. Unlike other force field formats, SMIRNOFF describes not only the parameters of the force field, but also the chemistries to which those parameters should be applied. 

This workshop introduces the SMIRNOFF format to familiar MD practitioners and describes how a system can be parametrized from a SMIRNOFF force field for a number of different MD engines. We hope to get both users and developers of molecular mechanics force fields excited about this game changing format.

First Session
: [Feb 20 23:00 UTC](https://time.is/1000_21_Feb_2024_in_Canberra/Tokyo/Auckland,_New_Zealand/Los_Angeles/Chicago/Phoenix/New_York/UTC?SMIRNOFF_OpenFF_Workshop)

: [💨 Join on Zoom](https://us06web.zoom.us/j/81208498403?pwd=m17ZJnzLDwXvLbInqDKdGoeImro0cC.1)

Second Session
: [Apr 10 12:00 UTC](https://time.is/2200_10_Apr_2024_in_Canberra/Beijing/Berlin/Los_Angeles/Chicago/Phoenix/New_York/London/UTC?SMIRNOFF_OpenFF_Workshop)

Zoom links will be published here 24 hours before the sessions begin.

Materials and Google Colab links can be found below.

**Goals:** Attendees will learn...
: That SMIRNOFF force fields are maps from arbitrary chemistry to a potential energy function
: That SMIRNOFF force fields can be combined to provide general coverage AND specific detail
: The basic format of a SMIRNOFF force field
: How to apply a collection of SMIRNOFF force fields to a ready-to-simulate box in PDB format
: That anyone can publish their SMIRNOFF force field (big or small) anywhere that distributes Python packages

**Non-goals:**
: How to prepare an MD system - this workshop focuses on force fields themselves and emphasizes conceptual understanding over application 
: Configuring BespokeFit for uses beyond Sage

**Assumed knowledge:**
: Basic working understanding of MD, force fields, structural biology
: Experience preparing MD systems and running simulations
: Some experience with Python helpful but not required

## Workshop Materials

This workshop is a live demonstration designed to be followed along with on your own computer. The entire workshop can be executed in your browser without installing anything using Google Colab:

[🤝 SMIRNOFF Workshop at Google Colab](https://colab.research.google.com/github/openforcefield/openff-docs/blob/main/source/workshops/2024/smirnoff/colab-smirnoff.ipynb)

For better performance and to keep any artifacts produced, you can install the relevant software locally and execute the notebook there. This requires an installation of Mamba, Micromamba, or similar conda-forge compatible package manager (see [](/install.md)). First, download the workshop materials:

[2024_smirnoff_workshop_materials.zip](path:smirnoff/2024_smirnoff_workshop_materials.zip)

Extract the zip file and open a terminal in the extracted directory. Then, create the environment:

```shell
mamba create -n smirnoff-workshop -f env.yml
```

And run Jupyter Lab in the new environment:

```shell
mamba run -n smirnoff-workshop jupyter-lab
```
