# Modelling with OpenFF

The OpenFF ecosystem is designed to slotted in to almost any molecular simulation workflow. We distribute both force fields themselves and Python tools to apply them, and our tools are compatible with a wide variety of chemical formats and MD engines. 

The basic OpenFF workflow consists of preparing a simulation system with the [OpenFF Toolkit] ([blue boxes]{.toolkit} in the flowchart below), and then exporting it to your MD engine of choice with [OpenFF Interchange] ([pink]{.interchange}):

(modelling-flowchart)=
{.deflist_flowchart}
- {.flowchart-sidebyside}
  - - Chemical Inputs
      : Molecular identities, coordinates, etc. We support [lots of formats]: SMILES, SDF, PDB, MOL/MOL2, RDKit `Mol`, OpenEye `OEGraphMol`,   NumPy Arrays...
  
    - []{.arrow-down}
  
    - {.toolkit-bg}
      OpenFF Toolkit [`Molecule`]
      : A molecular graph, with optional coordinates.
  
    - []{.arrow-down}
  
    - {.toolkit-bg}
      OpenFF Toolkit [`Topology`]
      : A collection of `Molecule` objects, with optional coordinates and   box vectors, representing a molecular system.
  
    - []{.arrow-down}

  - - {.optional}
      - {.bespokefit-bg}
        Torsion refinement with [OpenFF BespokeFit]
        : Automatic refinement of SMIRNOFF force field torsion parameters from quantum chemical calculations.
  
      - []{.arrow-cycle}
  
    - {.forcefield-bg}
      [SMIRNOFF Force Field]
      : We publish [our force fields] in an engine-agnostic [force field format] that parametrizes a   molecular graph without assigning atom types.
  
    - []{.arrow-down}
  
    - {.toolkit-bg}
      OpenFF Toolkit [`ForceField`]
      : Python representation of a SMIRNOFF force field, with tools for   inspection, modification, and storage.
  
    - []{.arrow-down}

- {.interchange-bg}
  OpenFF [`Interchange`]
  : A parametrized molecular simulation system, complete with force field parameters, chemical identities, box vectors, and coordinates, that can be [exported] to many different MD engines

- []{.arrow-cycle}

- MD Engines
  : OpenMM, GROMACS, Amber, CHARMM, LAMMPS...

[OpenFF Toolkit]: https://docs.openforcefield.org/projects/toolkit
[OpenFF Interchange]: https://docs.openforcefield.org/projects/interchange
[NumPy arrays]: numpy.array
[`Molecule`]: openff.toolkit.topology.Molecule
[`Topology`]: openff.toolkit.topology.Topology
[`ForceField`]: openff.toolkit.typing.engines.smirnoff.ForceField
[`Interchange`]: openff.interchange.Interchange
[lots of formats]: inv:openff.toolkit#users/molecule_cookbook
[OpenFF BespokeFit]: inv:openff.bespokefit#index
[SMIRNOFF Force Field]: ecosystem-smirnoff
[our force fields]: https://github.com/openforcefield/openff-forcefields
[force field format]: https://openforcefield.github.io/standards/standards/smirnoff/
[exported]: inv:openff.interchange#using/output

Check it out - preparing a molecule in vacuum for simulation in OpenMM just takes a few lines of Python:

```python
from openff.toolkit import Molecule, Topology, ForceField
from openff.interchange import Interchange

paracetamol = Molecule.from_smiles("CC(=O)NC1=CC=C(C=C1)O")
paracetamol.generate_conformers(n_conformers=1)

topology = Topology.from_molecules([paracetamol])

force_field = ForceField("openff-2.0.0.offxml")

interchange = Interchange.from_smirnoff(force_field, topology)

openmm_system = interchange.to_openmm()
openmm_topology = interchange.to_openmm_topology()
openmm_positions = interchange.positions.to_openmm()
```

(ecosystem-smirnoff)=
## [The SMIRNOFF Force Field Format]{.forcefield}

OpenFF force fields are published in the **SMIR**KS-**N**ative **O**pen **F**orce **F**ield format ([SMIRNOFF]). SMIRNOFF is a next-generation force field format that's intended to encode all the information needed to compute a potential energy from any molecule covered by the force field. SMIRNOFF records many important variables that are essential to reproducing the potential energy function used in fitting, but are missing from existing force field definition formats:

- The actual chemistry a parameter should be assigned to, which SMIRNOFF records with [SMIRKS strings]
- The non-bonded cutoff distance, combining rules, and long-range corrections (such as PME)
- The exact form of the function used for bonded terms
- Constraints that should be used with the force field, including those with hydrogens
- Non-bonded interactions between neighboring atoms that are excluded or scaled based on their through-bond connectivity
- The water model
- The model used to compute partial charges
- The model used to compute any implicit solvent

Many MD engines treat these as details of the simulation rather than of the force field, but varying them changes the potential energy of the system so we think they are best thought of as part of the force field. SMIRNOFF also does away with atom types: each parameter is just applied directly to the relevant atoms via a SMIRKS string. This means we can fine-tune a specific interaction without incurring the complexity cost of creating a new atom type or duplicating other parameters.

OpenFF maintains both the [SMIRNOFF format specification] as well as software tooling to apply SMIRNOFF force fields to systems for simulation in most mainstream MD engines. OpenFF's SMIRNOFF force fields are distributed in the [`openff-forcefields`] package ([green]{.forcefield} in the [flowchart]), and anyone can publish their own SMIRNOFF force field as described [in the FAQ]. The OpenFF Toolkit documentation [describes the SMIRNOFF format in more detail](inv:openff.toolkit#users/smirnoff).

[SMIRKS strings]: https://www.daylight.com/dayhtml/doc/theory/theory.smirks.html
[SMIRNOFF]: https://openforcefield.github.io/standards/standards/smirnoff/
[SMIRNOFF format specification]: https://openforcefield.github.io/standards/standards/smirnoff/
[flowchart]: modelling-flowchart
[`openff-forcefields`]: https://github.com/openforcefield/openff-forcefields
[in the FAQ]: https://docs.openforcefield.org/projects/toolkit/en/stable/faq.html#how-can-i-distribute-my-own-force-fields-in-smirnoff-format

(ecosystem-toolkit)=
## [Preparing a Simulation System]{.toolkit}

The [OpenFF Toolkit] provides tools for assembling chemical systems out of components prepared elsewhere. The pinnacle of this process is the [`Topology`] Python class. In OpenFF-speak, a topology is a model-agnostic collection of molecules, possibly in a box. It does not include any force field parameters or other model-specific values, and so can be easily parametrized and simulated with any force field. This makes comparative force field studies really easy, as you just prepare the topology once and can then parametrize it as many times as you like with any SMIRNOFF force field!

A topology is essentially a collection of `Molecule` objects with some extra system-level information like positions and box vectors. Molecules represent a single molecule as a molecular graph; atoms connected by bonds. We provide tools for loading both individual molecules and entire topologies from a wide variety of file formats. For details, see the [`Molecule`] and [`Topology`] API docs, and the [](inv:openff.toolkit#users/molecule_cookbook).

The OpenFF Toolkit avoids providing tools for system generation because we want to focus on what we're good at: making force fields better. But we encourage the wider modelling community to build tools for things like solvation, bilayer creation and docking on top of the OpenFF Toolkit!

The Toolkit also provides the [`ForceField`] class, which just loads a SMIRNOFF force field into Python-world. [](ecosystem-interchange) explains more on how that works.

The Toolkit is distributed in the [`openff-toolkit`] package and is represented in [blue]{.toolkit} on the [flowchart].

[`openff-toolkit`]: inv:openff.toolkit:*:doc#installation

(ecosystem-interchange)=
## [Parametrizing and Simulating]{.interchange}

[OpenFF Interchange] is our package for exporting simulation input data for an MD engine. The Interchange API mostly consists of the [`Interchange`] class, an instance of which represents a fully parametrized simulation system. You can call any of the `to_<format>` methods to [produce] input files to simulate that system in your MD engine of choice; OpenMM, Amber, GROMACS, and LAMMPS are all supported!

The main way to produce an `Interchange` is to combine a [`Topology`] with a [`ForceField`] using the [`Interchange.from_smirnoff()`] method. Interchange also implements a few other `from_<format>` methods that allow it to ingest parametrized systems from other MD engines! While these other formats usually do not provide enough information for Interchange to produce a [`Topology`] and then apply a different force field, Interchange can export the pre-parametrized system to other formats. So Interchange doesn't just export OpenFF stuff to MD engines, it also converts between MD engines!

Once you have your MD engine input files from Interchange, you just simulate them in the usual way --- most MD engines have excellent tutorials and documentation on how to do this. Interchange is distributed in the [`openff-interchange`] package and is represented in [pink]{.interchange} on the [flowchart].

[`Interchange.from_smirnoff()`]: openff.interchange.Interchange.from_smirnoff
[`openff-interchange`]: inv:openff.interchange:*:doc#installation
[produce]: inv:openff.interchange#using/output

(ecosystem-bespokefit)=
## [Fine-Tuning a Force Field]{.bespokefit}

Sometimes, general force fields like those we publish just aren't good enough, and you need to refine parameters for a new molecule. [OpenFF BespokeFit] is a tool that automatically identifies torsions that could use refinement, computes a quantum chemical torsion drive around those dihedrals, and refines a force field to reproduce that accurate torsion drive. It uses all sorts of clever tricks like fragmentation, multithreading, and caching to make this refinement fast, reproducible, and restartable, as well as to avoid repeating work on molecules that share chemistry. BespokeFit has the flexibility to work with a variety of quantum chemical engines via [QCEngine]. It uses a general SMIRNOFF force field as its starting point, and adds new terms to describe the new torsions. If you refine a torsion that's common to a line of molecules that you're interested in, you can use the resulting force field for the entire line!

BespokeFit uses a CLI interface to make it easy to use. It can be a bit involved, so to get started, see the [](inv:openff.bespokefit#getting-started/quick-start) or our [YouTube tutorial]. BespokeFit is distributed in the 
[`openff-bespokefit`] package and is represented in [orange]{.bespokefit} on the [flowchart].

[QCEngine]: https://github.com/MolSSI/QCEngine
[YouTube tutorial]: https://www.youtube.com/watch?v=jI1t7QGir98&t=1s&pp=ygUOb3BlbmZvcmNlZmllbGQ%3D
[`openff-bespokefit`]: inv:openff.bespokefit#getting-started/installation
