# The OpenFF Ecosystem

<style>
/*.deflist_flowchart {
  position: relative;
  width: 100%;
}
.deflist_flowchart dt {
  width: 40%;
  text-align: center;
  background-color: #f8f8f8;
  border-radius: 4px;
  box-shadow: 0 2px 2px 0 rgba(0,0,0,0.14),0 1px 5px 0 rgba(0,0,0,0.12),0 3px 1px -2px rgba(0,0,0,0.2);
  position: relative;
}

.deflist_flowchart dt:not(:first-child) {
  margin-top: 2em;
}


.deflist_flowchart dd {
  display: none;
  width: calc(100);
  height: 100%;
  position: absolute;
  right: 0;
  top: 0;
  margin: 0;
  padding: 0;
  margin-left: calc(40% + 1em);
}
.deflist_flowchart dt:hover + dd, 
.deflist_flowchart dd:hover, 
.deflist_flowchart dl:hover dd 
{
  display: block;
}

.deflist_flowchart dt:hover + dd > p:first-child, 
.deflist_flowchart dd:hover > p:first-child,
.deflist_flowchart dl:hover dd > p:first-child 
{
  margin-top: 0;
}

.deflist_flowchart dt:not(:first-child)::before {
  content: "↓";
  display: block;
  width: 100%;
  text-align: center;
  position: absolute;
  top: -2em;
}*/
:root {
    --arrow-thickness: 4px;
    --arrow-head-size: 7px;
    --arrow-length: 25px;
    --arrow-color: black;
}
.arrow.thick {
    --arrow-thickness: 6px;
    --arrow-head-size: 10px;
}

ul.deflist_flowchart,
ul.deflist_flowchart li,
ul.deflist_flowchart li ul,
ul.deflist_flowchart dl
{
  margin: 0;
  padding: 0;
}

.deflist_flowchart li {
  list-style: none;
}

.deflist_flowchart .arrow-down {
  display: block;
  width: 100%;
  height: 2em;

}

.deflist_flowchart .arrow-down::after,
.deflist_flowchart .arrow-cycle::after,
.deflist_flowchart .arrow-cycle::before
{
    width: calc(var(--arrow-length)/1.4142);
    height: calc(var(--arrow-length)/1.4142);
    content: "";
    padding: 0;
    display: inline-block;
    transform: rotate(45deg);
    background-image: linear-gradient(
      45deg,
      transparent calc(50% - var(--arrow-thickness)/2),
      var(--arrow-color) calc(50% - var(--arrow-thickness)/2),
      var(--arrow-color) calc(50% + var(--arrow-thickness)/2),
      transparent calc(50% + var(--arrow-thickness)/2)
    ), linear-gradient(
      -45deg,
      var(--arrow-color) var(--arrow-head-size),
      transparent var(--arrow-head-size)
    );
    margin-left: calc(50% - var(--arrow-head-size)/2);
}
.deflist_flowchart .arrow-cycle::before
{
    transform: rotate(-135deg);
    margin-left: calc(50% - 5*var(--arrow-head-size)/2);
}
.deflist_flowchart .arrow-cycle::after
{
    margin-left: calc(50% + 5*var(--arrow-head-size)/2);
}

.deflist_flowchart dl {
  text-align: center;
  background-color: #f8f8f8;
  border-radius: 4px;
  box-shadow: 0 2px 2px 0 rgba(0,0,0,0.14),0 1px 5px 0 rgba(0,0,0,0.12),0 3px 1px -2px rgba(0,0,0,0.2);
  position: relative;  
}

.deflist_flowchart dd {
  margin: 1em;
}

.deflist_flowchart dl.interchange-bg,
.deflist_flowchart dl.toolkit-bg,
.deflist_flowchart dl.bespokefit-bg ,
.deflist_flowchart dl.green-bg {
  color: whitesmoke;
}

.deflist_flowchart dl.interchange-bg a,
.deflist_flowchart dl.toolkit-bg a,
.deflist_flowchart dl.bespokefit-bg a,
.deflist_flowchart dl.green-bg a 
{
  color: whitesmoke;
  font-weight: bold;
}

.deflist_flowchart dl.interchange-bg a:hover,
.deflist_flowchart dl.toolkit-bg a:hover,
.deflist_flowchart dl.bespokefit-bg a:hover,
.deflist_flowchart dl.green-bg a:hover,
.deflist_flowchart dl.interchange-bg a:hover code,
.deflist_flowchart dl.toolkit-bg a:hover code,
.deflist_flowchart dl.bespokefit-bg a:hover code,
.deflist_flowchart dl.green-bg a:hover code 
{
  color: #2f9ed2;
}

.deflist_flowchart dl.interchange-bg a code,
.deflist_flowchart dl.toolkit-bg a code,
.deflist_flowchart dl.bespokefit-bg a code,
.deflist_flowchart dl.green-bg a code 
{
  color: #015480;
  font-weight: normal;
}

.deflist_flowchart dl.interchange-bg {
  background-color: #ee4266;
  color: whitesmoke;
}

.deflist_flowchart dl.toolkit-bg {
  background-color: #2f9ed2;
  color: whitesmoke;
}

.deflist_flowchart dl.bespokefit-bg {
  background-color: #F08521;
  color: whitesmoke;
}

.deflist_flowchart dl.green-bg {
  background-color: #04e762;
  color: whitesmoke;
}

ul.deflist_flowchart {
  display: grid;
  grid-template-areas: 
    "topology forcefield"
    "interchange interchange";
    grid-gap: 0 1em;
  align-items: end;
}

ul.deflist_flowchart > li:last-child {
  grid-area: interchange;
}

/*.deflist_flowchart li:has(> .grid-topology) {
  grid-area: topology;
}

.deflist_flowchart li:has(> .grid-forcefield) {
  grid-area: forcefield;

}

.deflist_flowchart li:has(> .grid-interchange) {  
  grid-area: interchange;
}*/
</style>

{.deflist_flowchart}
- {.grid-topology}
  - Chemical Inputs
    : Molecular identities, coordinates, etc. We support [lots of formats]: SMILES, SDF, PDB, MOL/MOL2, RDKit, OpenEye...

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

  - {.green-bg}
    [SMIRNOFF Force Field]
    : A [force field format] that relies on direct chemical perception.

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
