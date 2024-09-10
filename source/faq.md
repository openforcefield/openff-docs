# Frequently Asked Questions (FAQ)

## Getting Started

:::::{faq-entry} What do I need to know to get started?

OpenFF tools follow a philosophy of failing with a descriptive error message rather than trying to interpret intention from ambiguous information, so you
might find you have to provide more information than you're used to.
For an overview of how the ecosystem fits together, read [](modelling.md).
Once you're ready to start coding, check out [](install.md) and [](examples.md).

:::::

:::::{faq-entry} What kinds of input files can I apply SMIRNOFF parameters to?

SMIRNOFF force fields use direct chemical perception meaning that, unlike many molecular mechanics (MM) force fields, they apply parameters based on substructure searches acting directly on molecules.
This creates unique opportunities and allows them to encode a great deal of chemistry quite simply, but it also means that the *starting point* for parameter assignment must be well-defined chemically, giving not just the elements and connectivity for all of the atoms of all of the components of your system, but also providing the formal charges and bond orders.

Specifically, to apply SMIRNOFF to a system, you must either:
1. Provide Open Force Field Toolkit [`Molecule`] objects corresponding to the components of your system, or
2. Provide an OpenMM [`Topology`] which includes bond orders and thus can be converted to molecules corresponding to the components of your system

Without this information, our direct chemical perception cannot be applied to your molecule, as it requires the chemical identity of the molecules in your system -- that is, bond order and formal charge as well as atoms and connectivity.
Unless you provide the full chemical identity in this sense, we must attempt to guess or infer the chemical identity of your molecules, which is a recipe for trouble.
Different molecules can have the same chemical graph but differ in bond order and formal charge, or different resonance structures may be treated rather differently by some force fields (e.g. `c1cc(ccc1c2cc[nH+]cc2)[O-]` vs `C1=CC(C=CC1=C2C=CNC=C2)=O`, where the central bond is rotatable in one resonance structure but not in the other) even though they have identical formal charge and connectivity (chemical graph).
A force field which uses the chemical identity of molecules to assign parameters needs to know the exact chemical identity of the molecule you are intending to parameterize.

[`Molecule`]: openff.toolkit.topology.Molecule
[`Topology`]: openff.toolkit.topology.Topology

:::::

:::::{faq-entry} Can I use an Amber or GROMACS topology/coordinate file as a starting point for applying a SMIRNOFF force field?

Amber and GROMACS topologies and coordinate files do not include enough explicit chemical information to apply a SMIRNOFF force field.
For example, bond orders are not present in either format; one could infer bond orders based on bond lengths, or attempt to infer bond orders from force constants, but such inference work would be error-prone and is outside the scope of SMIRNOFF.
PDB files that include all atoms in the model can be used in some cases (see next question).

Amber and GROMACS topology and coordinate files can be [experimentally loaded] by Interchange for export to other MD engines, but this does not require the chemical information needed to apply a SMIRNOFF force field.

[experimentally loaded]: inv:openff.interchange#using/experimental

:::::

:::::{faq-entry} Can I use an Amber force field with SMIRNOFF ligands?

Experimental support for this approach is available through Interchange. Briefly, the ligands are parametrized in the usual SMIRNOFF way to produce an Interchange, the Amber components are parametrized through OpenMM and then loaded into a second Interchange with [`Interchange.from_openmm()`], and then the two Interchanges are combined.

[`Interchange.from_openmm()`]: openff.interchange.Interchange.from_openmm

:::::

:::::{faq-entry} What about starting from a PDB file?

PDB files are a ubiquitous coordinate format, but the interpretation of the chemistry of a given PDB file is ambiguous in many ways.
Without a complete and accurate chemical description of the system, SMIRNOFF parameters cannot be applied.
When a few common biopolymers like peptides have the conventional atom and residue names and are not missing any atoms, they can be loaded unambiguously.
However, different software packages in common use make slightly different choices for these conventions.
In addition, many of the affordances provided by the format for disambiguation, like formal charges and CONECT records, are both not reliably produced by all software and have deficiencies that make chemical identification impossible.
This means while PDBs are great for providing the coordinates of a known system of atoms in a format that can be readily visualized, applying SMIRNOFF parameters to them is an active area of development.

To load a PDB file including appropriately named canonical peptides with all atoms present and a known list of non-protein elements, see the OpenFF Toolkit's [PDB Cookbook].
This workflow is an active area of development and we are expanding the scope of what can be loaded as we settle on what is needed.

Given a PDB file of a hypothetical biomolecular system of interest containing a small molecule, there are several routes available to you for identifying the small molecules present:
- Use a cheminformatics toolkit (see below) to infer bond orders
- Identify your ligand from a database; e.g. if it is in the Protein Data Bank (PDB), it will be present in the [Ligand Expo](http://ligand-expo.rcsb.org) meaning that it has a database entry and code you can use to look up its putative chemical identity
- Identify your ligand by name or SMILES string (or similar) from the literature or your collaborators

[the PDB Cookbook]: inv:openff.toolkit#users/pdb_cookbook/index.ipynb

:::::

:::::{faq-entry} What about starting from an XYZ file?

XYZ files generally only contain elements and positions, and are therefore similar in content to PDB files. See the above section "What about starting from a PDB file?" for more information.

:::::

:::::{faq-entry} What do you recommend as a starting point?

For application of SMIRNOFF force fields, we recommend that you begin your work with formats which provide the chemical identity of your small molecule (including formal charge and bond order).
This means we recommend one of the following or equivalent:
- A `.sdf`, `.mol`, or `.mol2` file or files for the molecules comprising your system, with correct bond orders and formal charges. (Note: Do NOT generate this from a simulation package or tool which does not have access to bond order information; you may end up with a correct-seeming file, but the bond orders will be incorrect)
- Isomeric SMILES strings for the components of your system
- InChi strings for the components of your system
- Chemical Identity Registry numbers for the components of your system
- IUPAC names for the components of your system

Essentially, anything which provides the full identity of what you want to simulate (including stereochemistry) should work, though it may require more or less work to get it into an acceptable format.

:::::

:::::{faq-entry} How can I transfer my prepared system to HPC resources for simulation?

OpenFF recommends exporting a prepared `Interchange` to the target MD engine and using the MD engine's recommended method to transfer it to HPC resources. This way, no additional dependencies need to be installed on the HPC resource to use OpenFF tools during preparation. For most MD engines, simply transfer the files produced by the appropriate [`Interchange.to_*()`] methods. For OpenMM, create a `System` Python object with [`Interchange.to_openmm_system()`] or [`ForceField.create_openmm_system()`] and transfer it by [serializing to XML].

[`Interchange.to_*()`]: https://docs.openforcefield.org/projects/interchange/en/stable/_autosummary/openff.interchange.Interchange.html
[`Interchange.to_openmm_system()`]: https://docs.openforcefield.org/projects/interchange/en/stable/_autosummary/openff.interchange.Interchange.html#openff.interchange.Interchange.to_openmm_system
[`ForceField.create_openmm_system()`]: https://docs.openforcefield.org/projects/toolkit/en/stable/api/generated/openff.toolkit.typing.engines.smirnoff.ForceField.html#openff.toolkit.typing.engines.smirnoff.ForceField.create_openmm_system
[serializing to XML]: https://openmm.github.io/openmm-cookbook/latest/notebooks/cookbook/Saving%20Systems%20to%20XML%20Files.html
:::::

## Errors and Performance Issues

:::::{faq-entry} Why does partial charge assignment fail during conformer generation, even though my molecule has conformers?

Assigning partial charges with a quantum chemical method requires conformers, as they are an essential input to a quantum chemical calculation.
Because the charges assigned by a SMIRNOFF force field should be transferrable between systems, we default to generating our own set of conformers during charge assignment.
This requirement will become unnecessary for future SMIRNOFF force fields that use NAGL graph charges; see the [](#under-the-hood) section.

To assign charges based on the provided conformer if conformer generation fails, first assign charges, then use the assigned charges during parametrization:

```python
from openff.toolkit import ForceField, Topology, Molecule

topology = Topology.from_molecules([
    Molecule.from_smiles("C123C(C1)(C2)C3")
])
force_field  = ForceField("openff-2.2.0.offxml")
problematic_molecule_indices = [0]

for i in problematic_molecule_indices:
    molecule = topology.molecule(i)
    try:
        molecule.assign_partial_charges(
            partial_charge_method="am1bcc"
        )
    except ValueError:
        molecule.assign_partial_charges(
            partial_charge_method="am1bcc",
            use_conformers=molecule.conformers,
        )

interchange = force_field.create_interchange(
    topology,
    charge_from_molecules=[
        topology.molecule(i)
        for i in problematic_molecule_indices
    ]
)
```

:::::

:::::{faq-entry} I'm getting stereochemistry errors when loading a molecule from a SMILES string.

By default, the OpenFF Toolkit throws an error if a molecule with undefined stereochemistry is loaded. This is because the stereochemistry of a molecule may affect its partial charges, and assigning parameters using [direct chemical perception](https://pubs.acs.org/doi/pdf/10.1021/acs.jctc.8b00640) may require knowing the stereochemistry of chiral centers. In addition, coordinates generated by the Toolkit for undefined chiral centers may have any combination of stereochemistries; the toolkit makes no guarantees about consistency, uniformity, or randomness. Note that the main-line OpenFF force fields currently use a stereochemistry-dependent charge generation method, but do not include any other stereospecific parameters.

This behavior is in line with OpenFF's general attitude of requiring users to explicitly acknowledge actions that may cause silent errors later on. If you're confident a `Molecule` with unassigned stereochemistry is acceptable, pass `allow_undefined_stereo=True` to molecule loading methods like [Molecule.from_smiles](openff.toolkit.topology.Molecule.from_smiles) to downgrade the exception to a warning. For an example, see the "SMILES without stereochemistry" section in the [Molecule cookbook](smiles_no_stereochemistry). Where possible, our parameter assignment infrastructure will gracefully handle molecules with undefined stereochemistry that are loaded this way, though they will be missing any stereospecific parameters.

:::::

:::::{faq-entry} Parameterizing my system, which contains a large molecule, is taking forever. What's wrong?

The mainline OpenFF force fields use AM1-BCC to assign partial charges (via the `<ToolkitAM1BCCHandler>` tag in the OFFXML file). This method unfortunately scales poorly with the size of a molecule and ligands roughly 100 atoms (about 40 heavy atoms) or larger may take so long (i.e. 10 minutes or more) that it seems like your code is simply hanging indefinitely. If you have an OpenEye license and OpenEye Toolkits [installed](installation/openeye), the OpenFF Toolkit will instead use `quacpac`, which can offer better performance on large molecules. Otherwise, it uses AmberTools' `sqm`, which is free to use.

In the future, the use of AM1-BCC in OpenFF force fields may be replaced with method(s) that perform better and scale better with molecule size, but (as of April 2022) these are still in an experimental phase.

:::::

:::::{faq-entry} How can I silence warnings I'm expecting my code to generate?

OpenFF libraries often issue warnings when they detect that the user might be doing something they don't intend. These warnings are largely borne out of bug reports from users, and we'd rather make sure new users understand our software, so they can get noisy for experienced developers. We use the Python [`warnings`] module from the standard library, so warnings can be filtered from a particular section of code like so:

```python
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        category=openff.toolkit.utils.exceptions.AtomMappingWarning,
    )

    Molecule.from_smiles("[H:1][O:4][H:2]")
:::::

## Installation Issues

:::::{faq-entry} I'm having troubles installing the OpenFF Toolkit on my Apple Silicon Mac.

As of August 2022, some upstreams (at least AmberTools, possibly more) are not built on `osx-arm64`, so installing the OpenFF stack is only possible with [Rosetta]. See the [platform support] section of the installation documentation for more.

(Keywords `osx-arm64`, M1 Mac, M2 Mac)

[Rosetta]: https://support.apple.com/en-au/HT211861
[platform support]: install_arm

:::::

:::::{faq-entry} My mamba/conda installation of the toolkit doesn't appear to work. What should I try next?

We recommend that you install the toolkit in a fresh environment, explicitly passing the channels to be used, in-order:

```shell
mamba create -n <my_new_env> -c conda-forge openff-toolkit
mamba activate <my_new_env>
```

Installing into a new environment avoids forcing mamba to satisfy the dependencies of both the toolkit and all existing packages in that environment.
Taking the approach that conda/mamba environments are generally disposable, even ephemeral, minimizes the chances for hard-to-diagnose dependency issues.

:::::

:::::{faq-entry} My mamba/conda installation of the toolkit STILL doesn't appear to work.

Many of our users encounter issues that are ultimately due to their terminal finding a different `conda` at higher priority in their `PATH` than the `conda` deployment where OpenFF is installed. To fix this, find the conda deployment where OpenFF is installed. Then, if that folder is something like `~/miniconda3`, run in the terminal:

```shell
source ~/miniconda3/etc/profile.d/conda.sh
```

and then try rerunning and/or reinstalling the Toolkit.

:::::

## Under the Hood

:::::{faq-entry} How are partial charges assigned in a SMIRNOFF force field?

There are [many charge methods](https://openforcefield.github.io/standards/standards/smirnoff/#partial-charge-and-electrostatics-models) supported by the SMIRNOFF specification. With the exception of water, mainline OpenFF force fields only use AM1-BCC (through `ToolkitAM1BCC`) to assign partial charges. (A future biopolymer force field will likely use library charges for standard residues.)

If OpenEye Toolkits are installed and licensed, the ELF10 variant of AM1-BCC is used. OpenEye's Quacpac (`oequacpac.OEAM1BCCELF10Charges`) is used to generate partial charges.

Otherwise, RDKit is used to generate a conformer which is passed to AmberTool's `sqm` (with `-c bcc`).

Note that, because of differences with the ELF10 variant and other subtle differences between OpenEye Toolkits and RDKit/AmberTools, **assigned partial charges can be expected to differ** based on the available toolkit(s). These numerical differences are often minor but in some molecules or use cases can be significant.

A future charge method may use [NAGL](https://github.com/openforcefield/openff-nagl) to assign partial charges from a graph-convolutional neural network instead of an underlying semi-empirical method. This approach is anticipated to be faster, more scalable, and more consistent than current approaches. As of March 2024, this is under development and not released for general use.

:::::

:::::{faq-entry} I understand the risks and want to perform bond and formal charge inference anyway

If you are unable to provide a molecule in the formats recommended above and want to attempt to infer the bond orders and atomic formal charges, there are tools available elsewhere that can provide guesses for this problem. These tools are not perfect, and the inference problem itself is poorly defined, so you should review each output closely (see our [Core Concepts](users/concepts) for an explanation of what information is needed to construct an OpenFF Molecule). Some tools we know of include:

- the OpenEye Toolkit's [`OEPerceiveBondOrders`](https://docs.eyesopen.com/toolkits/python/oechemtk/OEChemFunctions/OEPerceiveBondOrders.html) functionality
- [MDAnalysis' RDKit converter](https://docs.mdanalysis.org/stable/documentation_pages/converters/RDKit.html?highlight=rdkit#module-MDAnalysis.converters.RDKit), with an [example here](https://github.com/openforcefield/openff-toolkit/issues/1126#issuecomment-969712195)
- the Jensen group's [xyz2mol program](https://github.com/jensengroup/xyz2mol/)

:::::

:::::{faq-entry} The partial charges generated by the toolkit don't seem to depend on the molecule's conformation! Is this a bug?

No! This is the intended behavior. The force field parameters of a molecule should be independent of both their chemical environment and conformation so that they can be used and compared across different contexts. When applying AM1BCC partial charges, the toolkit achieves a deterministic output by ignoring the input conformation and producing several new conformations for the same molecule. Partial charges are then computed based on these conformations. This behavior can be controlled with the `use_conformers` argument to [Molecule.assign_partial_charges()](openff.toolkit.topology.Molecule.assign_partial_charges).

:::::

## SMIRNOFF Force Fields

:::::{faq-entry} How can I distribute my own force fields in SMIRNOFF format?

We support conda data packages for distribution of force fields in `.offxml` format! Just add the relevant entry point to `setup.py` and distribute via a conda (or PyPI) package:

```python
entry_points={
    'openforcefield.smirnoff_forcefield_directory' : [
        'my_new_force_field_paths = my_package:get_my_new_force_field_paths',
    ],
}
```

Where `get_my_new_force_field_paths` is a function in the `my_package` module providing a list of strings holding the paths to the directories to search. You should also rename `my_new_force_field_paths` to suit your force field. See [`openff-forcefields`](https://github.com/openforcefield/openff-forcefields/blob/ed0d904/setup.py#L57-L61) for an example.

:::::

:::::{faq-entry} What does "unconstrained" mean in a force field name?

Each release of an [OpenFF force field](https://github.com/openforcefield/openff-forcefields/tree/main/openforcefields/offxml) has two associated `.offxml` files: one unadorned (for example, `openff-2.0.0.offxml`) and one labeled "unconstrained" (`openff_unconstrained-2.0.0.offxml`). This reflects the presence or absence of holonomic constraints on hydrogen-involving bonds in the force field specification.

Typically, OpenFF force fields treat bonds with a harmonic potential according to Hooke's law. With this treatment, bonds involving hydrogen atoms have a much higher vibration frequency than any other part of a typical biochemical system. By constraining these bonds to a fixed length, MD time steps can be increased past 1 fs, improving simulation performance. These bond vibrations are not structurally important to proteins so can usually be ignored.

While we recommend hydrogen-involving bond constraints and a time step of 2 fs for ordinary use, some other specialist uses require a harmonic treatment. The unconstrained force fields are provided for these uses.

Use the constrained force field:
 - When running MD with a time step greater than 1 fs

Use the unconstrained force field:
 - When computing single point energy calculations or energy minimization
 - When running MD with a time step of 1 fs (or less)
 - When bond lengths may deviate from equilibrium
 - When fitting a force field, both because many fitting techniques require continuity and because deviations from equilibrium bond length may be important
 - Any other circumstance when forces or energies must be defined or continuous for any possible position of a hydrogen atom

Starting with v2.0.0 (Sage), TIP3P water is included in OpenFF force fields. The geometry of TIP3P water is always constrained, even in the unconstrained force fields.

:::::

:::::{faq-entry} How do I add or remove constraints from my own force field?

To make applying or removing bond constraints easy, constrained force fields released by OpenFF always include full bond parameters. Constraints on Hydrogen-involving bonds inherit their lengths from the harmonic parameters also included in the force field. To restore the harmonic treatment, simply remove the appropriate constraint entry from the force field.

Hydrogen-involving bonds are constrained with a single constraint entry in a `.offxml` file:

```xml
<Constraints version="0.3">
    <!-- constrain all bonds to hydrogen to their equilibrium bond length -->
    <Constraint smirks="[#1:1]-[*:2]" id="c1"></Constraint>
</Constraints>
```

Adding or removing the inner `<Constraint...` line will convert a force field between being constrained and unconstrained. A [`ForceField`](openff.toolkit.typing.engines.smirnoff.forcefield.ForceField) object can constrain its bonds involving hydrogen by adding the relevant parameter to its `'Constraints'` parameter handler:

```python
ch = force_field.get_parameter_handler('Constraints')
ch.add_parameter({'smirks': "[#1:1]-[*:2]"})
```

:::::
