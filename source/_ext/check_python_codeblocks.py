#!/usr/bin/env python3
"""
Conditionally provide some variables to a wrapped script.

The purpose of this script is to provide the ability to quickly write short
snippets in the OpenFF documentation that do not require initialization of
common Toolkit objects while not inhibiting the quality of error messages from
more complete code examples.

Code examples are used throughout the docs and testing that they do not raise
errors has caught many documentation errors already. The `codelinter` Sphinx
extension runs this script on all code blocks in this documentation project.
The script sets up some commonly used variables and imports so that short
snippets don't have to initialize them, and then sets up an import hook that
deletes the added names if `openff.toolkit` is imported in the code block. This
means that short snippets can assume some common variables are in scope, but
long code blocks intended to be self-sufficient can opt out of this name
pollution by importing the toolkit.
"""

# Define the default namespace
import openff.toolkit
from openff.toolkit import ForceField, Molecule, Topology

molecule = Molecule.from_smiles("C123C(C1)(C2)C3")
topology = Topology.from_molecules([molecule])
force_field = ForceField("openff_unconstrained-2.2.0.offxml")
ff_unconstrained = force_field
ff_constrained = ForceField("openff-2.2.0.offxml")

# Set the import hook
import builtins
import sys

_old_import = __import__
_already_deleted = False


def __import__(name, *args, **kwargs):
    """
    Clear above variables on any new import of the toolkit
    """
    global _already_deleted
    if name.startswith("openff.toolkit") and not _already_deleted:
        global \
            molecule, \
            topology, \
            force_field, \
            ForceField, \
            Molecule, \
            Topology, \
            ff_constrained, \
            ff_unconstrained
        del (
            molecule,
            topology,
            force_field,
            ForceField,
            Molecule,
            Topology,
            ff_constrained,
            ff_unconstrained,
        )
        _already_deleted = True

    return _old_import(name, *args, **kwargs)


builtins.__import__ = __import__

# Execute the code block
exec(sys.stdin.read())
