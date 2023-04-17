# The OpenFF Ecosystem



<style>
:root {
    --arrow-thickness: 4px;
    --arrow-head-size: 7px;
    --arrow-length: 2em;
    --arrow-color: black;
}
.arrow.thick {
    --arrow-thickness: 6px;
    --arrow-head-size: 10px;
}

.content .deflist_flowchart p:first-child {
  margin-top: 0;
}

.content .deflist_flowchart p:last-child {
  margin-bottom: 0;
}

.content .deflist_flowchart,
.content .deflist_flowchart li,
.content .deflist_flowchart li ul,
.content .deflist_flowchart dl
{
  margin: 0;
  padding: 0;
}

.deflist_flowchart ul {
  display: flex;
  flex-direction: column;
  justify-content: stretch;
  height: 100%;
}

.content .deflist_flowchart li {
  list-style: none;
  flex-grow: 1;
  margin-top: 0.5em;
  margin-bottom: 0.5em;
}

.content .deflist_flowchart dl ul {
  display: block;
  height: unset;
  width: fit-content;
  margin: 0 auto;
}

.content .deflist_flowchart dl li {
  list-style: bullet;
  margin-left: 1.25em;
  text-align: left;
}

.content .deflist_flowchart li:first-child {
  margin-top: 0;
}

.content .deflist_flowchart li:last-child {
  margin-bottom: 0;
}

.deflist_flowchart .arrow-down,
.deflist_flowchart .arrow-up,
.deflist_flowchart .arrow-cycle {
  display: block;
  height: var(--arrow-length);
  margin-left: auto;
  margin-right: auto;
  width: fit-content;
}

.deflist_flowchart .arrow-down::after,
.deflist_flowchart .arrow-up::after,
.deflist_flowchart .arrow-cycle::after,
.deflist_flowchart .arrow-cycle::before
{
  height: calc(var(--arrow-length)/1.4142);
  width: auto;
  aspect-ratio: 1;
  content: "";
  padding: 0;
  display: inline-block;
  transform: rotate(45deg);
  background-image: 
    linear-gradient(
      45deg,
      transparent calc(50% - var(--arrow-thickness)/2),
      var(--arrow-color) calc(50% - var(--arrow-thickness)/2),
      var(--arrow-color) calc(50% + var(--arrow-thickness)/2),
      transparent calc(50% + var(--arrow-thickness)/2)
    ), 
    linear-gradient(
      -45deg,
      var(--arrow-color) var(--arrow-head-size),
      transparent var(--arrow-head-size)
    );
    margin: 0 calc(-0.5 * var(--arrow-length)/1.4142);
    margin-top: calc(1.4142 * var(--arrow-length) / 10);
}

.deflist_flowchart .arrow-cycle::after,
.deflist_flowchart .arrow-cycle::before
{
  margin: 0 calc(-0.5 * var(--arrow-length)/1.4142 + 10px);
  margin-top: calc(var(--arrow-length) / 7);
}

.deflist_flowchart .arrow-up::after,
.deflist_flowchart .arrow-cycle::before
{
    transform: rotate(-135deg);
}

.content .deflist_flowchart dl {
  text-align: center;
  background-color: #f8f8f8;
  border-radius: 4px;
  box-shadow: 0 2px 2px 0 rgba(0,0,0,0.14),0 1px 5px 0 rgba(0,0,0,0.12),0 3px 1px -2px rgba(0,0,0,0.2);
  position: relative;
  padding: 0.5em;
}

.deflist_flowchart dd {
  margin: 0;
  margin-top: 0.5em;
  padding: 0;
}

.deflist_flowchart dl.toolkit-bg,
.deflist_flowchart dl.forcefield-bg {
  color: whitesmoke;
}

.deflist_flowchart dl.toolkit-bg a,
.deflist_flowchart dl.forcefield-bg a 
{
  color: whitesmoke;
  font-weight: bold;
}

.deflist_flowchart dl a {
  font-weight: bold;
}

.deflist_flowchart dl.toolkit-bg a:hover,
.deflist_flowchart dl.forcefield-bg a:hover,
.deflist_flowchart dl.toolkit-bg a:hover code,
.deflist_flowchart dl.forcefield-bg a:hover code 
{
  color: #2f9ed2;
}

.deflist_flowchart dl.toolkit-bg a code,
.deflist_flowchart dl.forcefield-bg a code 
{
  color: #015480;
  font-weight: normal;
}

.deflist_flowchart dl.interchange-bg {
  background-color: #ee4266;
}

.deflist_flowchart dl.toolkit-bg {
  background-color: #2f9ed2;
}

.deflist_flowchart dl.bespokefit-bg {
  background-color: #F08521;
}

.deflist_flowchart dl.forcefield-bg {
  background-color: #04e762;
}

.content .deflist_flowchart {
  display: grid;
  grid-template-areas: 
    "topology forcefield"
    "interchange interchange";
    grid-gap: 0 1em;
  align-items: stretch;
}

@supports not selector(:has(a, b)) {
  /* Fallback for when :has() is unsupported */
  ul.deflist_flowchart > li:last-child {
    grid-area: interchange;
  }
}

.deflist_flowchart li:has(> .grid-topology) {
  grid-area: topology;
}

.deflist_flowchart li:has(> .grid-forcefield) {
  grid-area: forcefield;

}

.deflist_flowchart li:has(> .grid-interchange) {  
  grid-area: interchange;
}

</style>

{.deflist_flowchart}
- {.grid-topology}
  - Chemical Inputs
    : Molecular identities, coordinates, etc. We support [lots of formats]: SMILES, SDF, PDB, MOL/MOL2, RDKit `Mol`, OpenEye `OEGraphMol`, NumPy Arrays...

  - []{.arrow-down}

  - {.toolkit-bg}
    OpenFF Toolkit [`Molecule`]
    : A molecular graph, with optional coordinates

  - []{.arrow-down}

  - {.toolkit-bg}
    OpenFF Toolkit [`Topology`]
    : A collection of `Molecule` objects

  - []{.arrow-down}

- {.grid-forcefield}
  - {.bespokefit-bg}
    Torsion refinement with [OpenFF BespokeFit]
    : Automatic refinement of SMIRNOFF force field torsion parameters from quantum chemical calculations

  - []{.arrow-cycle}

  - {.forcefield-bg}
    [SMIRNOFF Force Field]
    : An engine-agnostic [force field format] that parametrizes a molecular graph without assigning atom types.

  - []{.arrow-down}

  - {.toolkit-bg}
    OpenFF Toolkit [`ForceField`]
    : Python representation of a SMIRNOFF force field

  - []{.arrow-down}

- {.grid-interchange}
  - {.interchange-bg}
    OpenFF [`Interchange`]
    : A parametrized molecular simulation system, complete with force field parameters, chemical identities, box vectors, and coordinates, that can be exported to many different MD engines

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
