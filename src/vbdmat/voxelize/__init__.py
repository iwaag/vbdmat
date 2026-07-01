"""Dense reference voxelization of watertight single-solid meshes (ADR-006)."""

from .errors import MeshTopologyError, VoxelizationError
from .mesh import (
    SUPPORTED_MESH_UNITS,
    VoxelizationDiagnostics,
    VoxelizationResult,
    inspect_topology,
    voxelize_mesh,
)

__all__ = [
    "SUPPORTED_MESH_UNITS",
    "MeshTopologyError",
    "VoxelizationDiagnostics",
    "VoxelizationError",
    "VoxelizationResult",
    "inspect_topology",
    "voxelize_mesh",
]
