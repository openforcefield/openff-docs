# The OpenFF Ecosystem

{.deflist_flowchart}
- {.grid-topology}
  - Chemical Inputs
    : Molecular identities, coordinates, etc. We support [lots of formats]: SMILES, SDF, PDB, MOL/MOL2, RDKit `Mol`, OpenEye `OEGraphMol`, NumPy Arrays...

  - []{.arrow-down}

  - {.toolkit-bg}
    OpenFF Toolkit [`Molecule`]
    : A molecular graph, with optional coordinates.

  - []{.arrow-down}

  - {.toolkit-bg}
    OpenFF Toolkit [`Topology`]
    : A collection of `Molecule` objects, with optional coordinates and box vectors, representing a molecular system.

  - []{.arrow-down}

- {.grid-forcefield}
  - {.bespokefit-bg}
    Torsion refinement with [OpenFF BespokeFit]
    : Automatic refinement of SMIRNOFF force field torsion parameters from quantum chemical calculations

  - []{.arrow-cycle}

  - {.forcefield-bg}
    [SMIRNOFF Force Field]
    : An engine-agnostic [force field format] that parametrizes a molecular graph without assigning atom types.

  - []{.arrow-down}

  - {.toolkit-bg}
    OpenFF Toolkit [`ForceField`]
    : Python representation of a SMIRNOFF force field, with tools for inspection, modification, and storage.

  - []{.arrow-down}

- {.grid-interchange}
  - {.interchange-bg}
    OpenFF [`Interchange`]
    : A parametrized molecular simulation system, complete with force field parameters, chemical identities, box vectors, and coordinates, that can be [exported] to many different MD engines

  - []{.arrow-cycle}

  - MD Engines
    : OpenMM, GROMACS, Amber, CHARMM, LAMMPS...

[NumPy arrays]: numpy.array
[`Molecule`]: openff.toolkit.topology.Molecule
[`Topology`]: openff.toolkit.topology.Topology
[`ForceField`]: openff.toolkit.typing.engines.smirnoff.ForceField
[`Interchange`]: openff.interchange.Interchange
[lots of formats]: inv:openff.toolkit#users/molecule_cookbook
[OpenFF BespokeFit]: inv:openff.bespokefit#index
[SMIRNOFF Force Field]: https://github.com/openforcefield/openff-forcefields
[force field format]: https://openforcefield.github.io/standards/standards/smirnoff/
[exported]: inv:openff.interchange#using/output
