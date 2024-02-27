from dataclasses import dataclass, field
from pathlib import Path
from os import PathLike
import tempfile
import MDAnalysis as mda
import nglview
from openff.toolkit import Molecule, Topology
from typing import Iterable
import subprocess
import openmm.app
from io import StringIO
from typing import Literal
from itertools import cycle
from copy import deepcopy
from nglview import show_text, NGLWidget
from openmm.app import PDBFile
import openmm
from pdbfixer import PDBFixer
from openff.units import unit
import numpy
import mdtraj

# TODO: Require (or at least support) units throughout

def fixer_to_string(fixer):
    with StringIO() as file:
        PDBFile.writeFile(fixer.topology, fixer.positions, file)
        pdb_string = file.getvalue()
    return pdb_string
    

def set_representations(
    widget: NGLWidget,
    representations: Literal['defaults', 'cartoononly', 'linesonly', 'licoriceonly', 'withunitcell', None]='defaults', 
):
    widget.clear_representations()
    if representations in ['defaults', 'withunitcell'] :
        widget.add_representation('cartoon', colorScheme='atomindex', selection='protein')
        widget.add_representation('spacefill', selection='not protein and not water')
        widget.add_representation('licorice', selection='water')
        if representations == 'withunitcell':
            widget.add_representation('unitcell')
    elif representations == 'cartoononly':        
        widget.add_representation('cartoon', colorScheme='atomindex', selection='protein')
    elif representations == 'linesonly':        
        widget.add_representation('line')
    elif representations == 'licoriceonly':        
        widget.add_representation('licorice')
    elif representations is not None:
        raise ValueError(f"Unknown representations {representations}")

    return widget

def show_fixer(
    fixer: PDBFixer, 
    representations: Literal['defaults', 'cartoononly']='defaults', 
    *args, 
    **kwargs
):
    widget = show_text(fixer_to_string(fixer), *args, **kwargs)
    set_representations(widget, representations)
    return widget

def nglview_show_openmm(topology: openmm.app.Topology, positions, image_molecules=False):
    import mdtraj
    import openmm.unit
    import nglview
    
    top = mdtraj.Topology.from_openmm(topology)

    if isinstance(positions, str) or isinstance(positions, Path):
        traj = mdtraj.load(positions, top=top)
        if image_molecules:
            traj.image_molecules(inplace=True)
    else:
        positions = ensure_quantity(positions, "openmm").value_in_unit(
            openmm.unit.nanometer
        )
        xyz = numpy.asarray([positions])
        box_vectors = topology.getPeriodicBoxVectors()
        if box_vectors is not None:
            (
                l1,
                l2,
                l3,
                alpha,
                beta,
                gamma,
            ) = mdtraj.utils.box_vectors_to_lengths_and_angles(
                *numpy.asarray(box_vectors.value_in_unit(openmm.unit.nanometer))
            )
            unitcell_angles, unitcell_lengths = [alpha, beta, gamma], [l1, l2, l3]
        else:
            unitcell_angles, unitcell_lengths = None, None
        traj = mdtraj.Trajectory(
            xyz, top, unitcell_lengths=unitcell_lengths, unitcell_angles=unitcell_angles
        )
    return nglview.show_mdtraj(traj)

def check_missing_residues(fixer) -> tuple[NGLWidget, str, str]:
    widget = show_fixer(fixer, 'cartoononly')
    
    colors = cycle(['red', 'green', 'blue', 'purple', 'yellow', 'grey', 'orange', 'black'])

    # Header for table
    print(f"{'Color': <10} {'Chain': <8} {'Residue': <8} Loop")
    print('-' * 80)
    
    missing_loops_selection = []
    missing_resis_selection = []
    added_resis = 0
    for color, ((chainindex, resindex), to_insert) in zip(colors, fixer.missingResidues.items()):
        chainid = [*fixer.topology.chains()][chainindex].id
    
        # Display the ends of the missing loops
        print(f"{color: <10} {chainid: <8} {resindex: <8} [{', '.join(to_insert)}]")
        widget.add_representation(
            "spacefill", 
            selection=f"({resindex} or {resindex+1}) and :{chainid}.CA",
            color=color,
        )
    
        # Build a selection string for the residues we're about to add
        loop_start = resindex + added_resis + 1
        loop_end = resindex + added_resis + len(to_insert)

        missing_loops_selection.append(f"{loop_start}-{loop_end}:{chainid}")
        
        added_resis += len(to_insert)
        
    missing_loops_selection = " or ".join(missing_loops_selection)
    
    return widget, missing_loops_selection

@dataclass(kw_only=True)
class DockTarget:
    name: str
    receptor: str | mda.Universe # If a str is provided, that's the contents of the PDBQT that gets used; clever stuff like water removal from search space only happens for universes.
    pdbfile: PDBFile
    center: None | tuple[float, float, float]
    size: None | tuple[float, float, float]
    working_dir: Path | None = None
    _target_dir: tempfile.TemporaryDirectory = field(
        default_factory=tempfile.TemporaryDirectory, 
        init=False, 
        repr=False,
        compare=False,
    )

    @classmethod
    def from_pdbqt(
        cls, 
        filename: str | Path,
        *,
        center: None | tuple[float, float, float] = None,
        size: None | tuple[float, float, float] = None,
        working_dir: PathLike | str | None = None,
    ) -> "DockTarget":
        filename = Path(filename)
        return cls(
            name = filename.stem,
            receptor = filename.read_string(),
            pdbfile = PDBFile(str(filename)),
            center = None if center is None else tuple(center),
            size = None if size is None else tuple(size),
            working_dir = None if working_dir is None else Path(working_dir),
        )
        
        
    @classmethod
    def from_pqr(
        cls, 
        filename: str | Path,
        *,
        center: None | tuple[float, float, float] = None,
        size: None | tuple[float, float, float] = None,
        working_dir: PathLike | str | None = None,
    ) -> "DockTarget":
        filename = Path(filename)
        # Convert to pdbqt with openbabel
        # This assigns atom types and drops nonpolar hydrogens, but loses partial charges
        # TODO: Calculate charges with obabel? I think pdb2pqr's charges are probably OK
        with tempfile.NamedTemporaryFile(suffix='.pdbqt') as f:
            # !obabel -ipqr {filename} -opdbqt -O{f.name} -xr
            subprocess.run(
                ['obabel', '-ipqr', filename, '-opdbqt', f'-O{f.name}',  '-xr'],
                capture_output=True,
                check=True,
            )
            u = mda.Universe(f.name)

        # OBabel drops charges, so pick them back up
        u_from_pqr = mda.Universe(filename)
        for atom in u.atoms:
            pqr_atomgroup = u_from_pqr.select_atoms(
                f"resname {atom.residue.resname} and resid {atom.residue.resid} and name {atom.name}"
            )
            assert len(pqr_atomgroup) == 1, f"expect only one atom, got {len(pqr_atomgroup)}"
            atom.charge = pqr_atomgroup[0].charge
        
        return cls(
            name = filename.stem,
            receptor = u,
            pdbfile = PDBFile(str(filename)),
            center = None if center is None else tuple(center),
            size = None if size is None else tuple(size),
            working_dir = None if working_dir is None else Path(working_dir),
        )
        
        
    @classmethod
    def from_pdb(
        cls, 
        filename: str | Path,
        *,
        center: None | tuple[float, float, float] = None,
        size: None | tuple[float, float, float] = None,
        working_dir: PathLike | str | None = None,
    ) -> "DockTarget":
        filename = Path(filename)
        # Convert to pdbqt with openbabel
        # This assigns atom types and drops nonpolar hydrogens, but loses partial charges
        with tempfile.NamedTemporaryFile(suffix='.pdbqt') as f:
            subprocess.run(
                ['obabel', '--partialcharge', 'gasteiger', '-ipdb', filename, '-opdbqt', f'-O{f.name}',  '-xr'],
                capture_output=True,
                check=True,
            )
            u = mda.Universe(f.name)
        
        return cls(
            name = filename.stem,
            receptor = u,
            pdbfile = PDBFile(str(filename)),
            center = None if center is None else tuple(center),
            size = None if size is None else tuple(size),
            working_dir = None if working_dir is None else Path(working_dir),
        )

            
    def get_conf_str(self) -> str:
        conf =  {
            'center_x': self.center[0],
            'center_y': self.center[1],
            'center_z': self.center[2],
            'size_x': self.size[0],
            'size_y': self.size[1],
            'size_z': self.size[2],
        }
        return "\n".join(f"{k} = {v}" for k, v in conf.items())

    def dock(self, ligand: str | Molecule, *args, **kwargs):
        try:
            smiles = ligand.to_smiles()
        except AttributeError:
            smiles = str(ligand)

        if self.working_dir is not None:
            self.working_dir.mkdir(parents=True, exist_ok=True)
            
        with self as target:
            score, aux = target.dock(smiles, *args, **kwargs)
        
        return DockResult.from_docktarget(score, aux, self)

    def visualize(self):
        if isinstance(self.receptor, str):
            w = nglview_show_openmm(self.pdbfile.topology, self.pdbfile.positions)
        elif isinstance(self.receptor, mda.Universe):
            w = nglview.show_mdanalysis(self._atoms_except_waters_in_search_space())
        else:
            raise TypeError("self.receptor should be Universe or str")
        
        w.clear_representations()
        w.add_licorice(selection='not protein')
        w.add_cartoon(color='atomindex')

        if self.center and self.size:
            x = [self.center[0] - self.size[0]/2, self.center[0] + self.size[0]/2]
            y = [self.center[1] - self.size[1]/2, self.center[1] + self.size[1]/2]
            z = [self.center[2] - self.size[2]/2, self.center[2] + self.size[2]/2]
            color = [1, 0, 0.7]
            radius = 0.5
            args = [color, radius]
                
            w.shape.add_arrow([x[0], y[0], z[0]], [x[0], y[0], z[1]], *args)
            w.shape.add_arrow([x[0], y[0], z[0]], [x[0], y[1], z[0]], *args)
            w.shape.add_arrow([x[0], y[0], z[0]], [x[1], y[0], z[0]], *args)
                
            w.shape.add_arrow([x[1], y[1], z[1]], [x[0], y[1], z[1]], *args)
            w.shape.add_arrow([x[1], y[1], z[1]], [x[1], y[0], z[1]], *args)
            w.shape.add_arrow([x[1], y[1], z[1]], [x[1], y[1], z[0]], *args)
    
            w.shape.add_arrow([x[1], y[0], z[1]], [x[0], y[0], z[1]], *args)
            w.shape.add_arrow([x[0], y[1], z[1]], [x[0], y[0], z[1]], *args)
            
            w.shape.add_arrow([x[0], y[1], z[1]], [x[0], y[1], z[0]], *args)
            w.shape.add_arrow([x[1], y[1], z[0]], [x[0], y[1], z[0]], *args)
            
            w.shape.add_arrow([x[1], y[1], z[0]], [x[1], y[0], z[0]], *args)
            w.shape.add_arrow([x[1], y[0], z[1]], [x[1], y[0], z[0]], *args)
    
            w.shape.add_arrow([0,0,0], [10,0,0], [1,0,0], 0.25)
            w.shape.add_text([10,0,0], [0,0,0], 10, "x")
            w.shape.add_arrow([0,0,0], [0,10,0], [0,1,0], 0.25)
            w.shape.add_text([0,10,0], [0,0,0], 10, "y")
            w.shape.add_arrow([0,0,0], [0,0,10], [0,0,1], 0.25)
            w.shape.add_text([0,0,10], [0,0,0], 10, "z")
        
        return w


    def __enter__(self):
        """Create a Dockstring Target for docking"""
        from dockstring.target import Target
        
        target_dir_path = Path(self._target_dir.__enter__())

        pdbqt_path = target_dir_path / f"{self.name}_target.pdbqt"
        pdbqt_path.write_text(self.pdbqt)

        conf = target_dir_path / f"{self.name}_conf.txt"
        conf.write_text(self.get_conf_str())
        
        return Target(
            name = self.name,
            working_dir = self.working_dir,
            targets_dir = target_dir_path,
        )

    def __exit__(self, type, value, tb):
        ret = self._target_dir.__exit__(type, value, tb)
        self._target_dir = tempfile.TemporaryDirectory()
        return ret

    def _atoms_except_waters_in_search_space(self):
        if not (self.center and self.size):
            return self.receptor.atoms
        selection = ' and '.join([
            "resname HOH",
            f"prop x >= {self.center[0] - self.size[0]/2}",
            f"prop x <= {self.center[0] + self.size[0]/2}",
            f"prop y >= {self.center[1] - self.size[1]/2}",
            f"prop y <= {self.center[1] + self.size[1]/2}",
            f"prop z >= {self.center[2] - self.size[2]/2}",
            f"prop z <= {self.center[2] + self.size[2]/2}",
        ])
        return self.receptor.select_atoms(f"not (same residue as ({selection}))")

    @property
    def pdbqt(self):
        if isinstance(self.receptor, str):
            return self.receptor
        elif isinstance(self.receptor, mda.Universe):
            with tempfile.NamedTemporaryFile(suffix=".pdbqt") as f:
                pdbqt_path = Path(f.name)
                self._atoms_except_waters_in_search_space().write(pdbqt_path)
                # MDA writes CRYST1 and FRAME lines up front, 
                # but Vina doesn't like them, so skip first two lines
                return "\n".join(pdbqt_path.read_text().splitlines()[2:])
                
        else:
            raise TypeError("self.receptor should be Universe or str")
    

@dataclass(kw_only=True)
class DockResult:
    ligand: Molecule
    scores: list[float]
    target: DockTarget
    aux: dict

    @classmethod
    def from_docktarget(cls, score, aux, target) -> 'DockResult':
        return cls(
            ligand=Molecule.from_rdkit(aux.pop('ligand')),
            scores=aux.pop('affinities'),
            aux=aux,
            target=target,
        )
        
    def visualize(self):
        self.target.pdbfile.topology
        traj = mdtraj.Trajectory(
            [self.target.pdbfile.positions.value_in_unit(openmm.unit.nanometer)], 
            mdtraj.Topology.from_openmm(self.target.pdbfile.topology),
        )
        
        w = self.ligand.visualize(backend='nglview')
        w.add_component(nglview.MDTrajTrajectory(traj))
        
        return w

    @staticmethod
    def _consolidate_water_chains(omm_top: openmm.app.Topology) -> openmm.app.Topology:
        new = openmm.app.Topology()
        water_chain = None
        for chain in omm_top.chains():
            if all(residue.name=='HOH' for residue in chain.residues()):
                if water_chain is None:
                    water_chain = new.addChain(chain.id)
                new_chain = water_chain
            else:
                new_chain = new.addChain(chain.id)
                
            for residue in chain.residues():
                new_residue = new.addResidue(
                    residue.name,
                    new_chain,
                    residue.id,
                    residue.insertionCode
                )
                
                for atom in residue.atoms():
                    new.addAtom(atom.name, atom.element, new_residue, atom.id)
        new_atoms = [*new.atoms()]
        
        for bond in omm_top.bonds():
            new.addBond(
                new_atoms[bond.atom1.index],
                new_atoms[bond.atom2.index],
                bond.type,
                bond.order,
            )

        box = omm_top.getPeriodicBoxVectors()
        if box is not None:
            new.setPeriodicBoxVectors(box)

        return new
                

    def to_openmm(self, pose: int = 0) -> tuple[openmm.app.Topology, openmm.unit.Quantity]:
        topology = self._consolidate_water_chains(self.target.pdbfile.topology)
        positions = numpy.concatenate(
            (
                self.target.pdbfile.positions.value_in_unit(openmm.unit.nanometer),
                self.ligand.conformers[pose].to_openmm().value_in_unit(openmm.unit.nanometer)
            ), 
            axis=0,
        ) * openmm.unit.nanometer

        ligand_chain = topology.addChain()
        ligand_residue = topology.addResidue('UNK', ligand_chain)
        ligand = Molecule(self.ligand)
        ligand.generate_unique_atom_names()
        atoms = {}
        for atom in ligand.atoms:
            atoms[atom] = topology.addAtom(
                atom.name, 
                openmm.app.Element.getBySymbol(atom.symbol), 
                ligand_residue
            )
        for bond in ligand.bonds:
            topology.addBond(atoms[bond.atom1], atoms[bond.atom2], order=bond.bond_order)

        return topology, positions    

    def to_pdbfixer(self, pose: int = 0):    
        with StringIO() as f:
            PDBFile.writeFile(*self.to_openmm(pose=pose), f)
            f.seek(0)
            fixer = PDBFixer(pdbfile=f)
        
        return fixer
