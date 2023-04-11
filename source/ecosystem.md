# The OpenFF Ecosystem

<style>
dl.deflist_flowchart {
  position: relative;
  width: 100%;
}
dl.deflist_flowchart dt {
  width: 40%;
  text-align: center;
  background-color: #f8f8f8;
  border-radius: 4px;
  box-shadow: 0 2px 2px 0 rgba(0,0,0,0.14),0 1px 5px 0 rgba(0,0,0,0.12),0 3px 1px -2px rgba(0,0,0,0.2);
  position: relative;
}

dl.deflist_flowchart dt:not(:first-child) {
  margin-top: 2em;
}


dl.deflist_flowchart dd {
  display: none;
  width: calc(60% - 1em);
  height: 100%;
}
dl.deflist_flowchart dt:hover + dd, dl.deflist_flowchart dd:hover {
  display: block;
  position: absolute;
  right: 0;
  top: 0;
  margin: 0;
  padding: 0;
}

dl.deflist_flowchart dt:hover + dd > p:first-child, dl.deflist_flowchart dd:hover > p:first-child {
  margin-top: 0;
}

dl.deflist_flowchart dt:not(:first-child)::before {
  content: "↓";
  display: block;
  width: 100%;
  text-align: center;
  position: absolute;
  top: -2em;
}
</style>

{.deflist_flowchart}
Chemical Identities
: &ZeroWidthSpace;
  OpenFF tools require the chemical identity of an entire molecule to satisfy some basic valence rules in order to parametrize it. This is in contrast to other tools that work on identifying individual residues or bla. Requiring chemical identities often lets us tell you that you're making a mistake, rather than letting you find out when you get nonsensical results back from the supercomputer.
  
  The OpenFF Toolkit can ingest chemical identities in the form of SDF files or SMILES strings, can infer chemical identities from PDB files, or a number of other sources. For more, see the [](inv:openff.toolkit#users/molecule_cookbook).

Atom Coordinates
: OpenFF can help keep all your data in one workflow by keeping track of atomic coordinates. Coordinates are stored as [NumPy arrays]

`Molecule`
: The [`Molecule`] class

`Topology`
: The [`Topology`] class

SMIRNOFF force field
: The SMIRNOFF force field format

`ForceField`
: The [`ForceField`] class

`Interchange`
: The [`Interchange`] class

BespokeFit
: OpenFF BespokeFit is a tool

[NumPy arrays]: numpy.array
[`Molecule`]: openff.toolkit.topology.Molecule
[`Topology`]: openff.toolkit.topology.Topology