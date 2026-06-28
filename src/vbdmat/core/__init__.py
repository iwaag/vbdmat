"""Canonical data definitions shared by all VBDMAT modules."""

from .geometry import GridGeometry
from .materials import MaterialDefinition, MaterialPalette, MaterialRole
from .metadata import VOLUME_SCHEMA, Provenance, SchemaIdentity, SchemaVersion
from .optical_basis import OpticalBasis, OpticalBasisKind

__all__ = [
    "VOLUME_SCHEMA",
    "GridGeometry",
    "MaterialDefinition",
    "MaterialPalette",
    "MaterialRole",
    "OpticalBasis",
    "OpticalBasisKind",
    "Provenance",
    "SchemaIdentity",
    "SchemaVersion",
]
