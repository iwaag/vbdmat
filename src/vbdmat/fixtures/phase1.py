"""Deterministic Phase 1 representative input fixtures (plan Step 4).

Two reviewable, analytically specified inputs exercise the Phase 1 readers end to
end without opaque binaries:

* a **multi-material window coupon** for the direct ``vbdmat.voxels/1.0.0`` path
  (a transparent matrix with one white inclusion and one asymmetric black marker);
* a **single-material stepped wedge** for the mesh path (a watertight staircase with
  analytically predictable per-step occupancy).

Every generator is pure and deterministic. The expected summaries here are derived
analytically from the fixture *definition*, not from the reader/voxelizer under
test, so a test comparing reader output to these values is a genuine check.
"""

from __future__ import annotations

import hashlib
import io
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from vbdmat.core import (
    MaterialDefinition,
    MaterialPalette,
    MaterialRole,
)

PHASE1_FIXTURE_GENERATOR = "vbdmat.fixtures.phase1"
PHASE1_FIXTURE_GENERATOR_VERSION = "1.0.0"

# --------------------------------------------------------------------------- #
# Multi-material window coupon (direct-voxel path)
# --------------------------------------------------------------------------- #

_COUPON_SHAPE_ZYX = (12, 16, 20)
_COUPON_VOXEL_SIZE_XYZ_M = (0.0005, 0.0004, 0.0003)
_COUPON_TRANSLATION_M = (0.010, 0.020, 0.030)
# Non-symmetric feature boxes given as [z, y, x] half-open index ranges so an
# accidental transpose or axis flip relocates them and fails the checks.
_COUPON_WHITE_ZYX = ((2, 5), (3, 7), (4, 10))
_COUPON_BLACK_ZYX = ((8, 10), (11, 14), (15, 18))

COUPON_MANIFEST_NAME = "window_coupon.voxels.json"
COUPON_PAYLOAD_NAME = "window_coupon.material_id.npy"


@dataclass(frozen=True, slots=True)
class BoxRegion:
    """A half-open ``[z, y, x]`` index box and the material it carries."""

    material_id: int
    z: tuple[int, int]
    y: tuple[int, int]
    x: tuple[int, int]

    @property
    def cell_count(self) -> int:
        """Return the number of cells in the box."""
        return (
            (self.z[1] - self.z[0])
            * (self.y[1] - self.y[0])
            * (self.x[1] - self.x[0])
        )

    @property
    def min_corner_zyx(self) -> tuple[int, int, int]:
        """Return the inclusive minimum ``[z, y, x]`` index of the box."""
        return (self.z[0], self.y[0], self.x[0])


@dataclass(frozen=True, slots=True)
class CouponSummary:
    """Analytic, implementation-independent expectations for the coupon."""

    shape_zyx: tuple[int, int, int]
    voxel_size_xyz_m: tuple[float, float, float]
    local_to_world_translation_m: tuple[float, float, float]
    material_counts: dict[int, int]
    white_inclusion: BoxRegion
    black_marker: BoxRegion
    bounds_min_xyz_m: tuple[float, float, float]
    bounds_max_xyz_m: tuple[float, float, float]
    payload_sha256: str


def window_coupon_label() -> npt.NDArray[np.uint16]:
    """Return the deterministic coupon label array (``uint16[z, y, x]``)."""
    label = np.ones(_COUPON_SHAPE_ZYX, dtype=np.uint16)  # transparent matrix
    (wz, wy, wx) = _COUPON_WHITE_ZYX
    label[wz[0] : wz[1], wy[0] : wy[1], wx[0] : wx[1]] = 2  # white inclusion
    (bz, by, bx) = _COUPON_BLACK_ZYX
    label[bz[0] : bz[1], by[0] : by[1], bx[0] : bx[1]] = 3  # black marker
    return label


def window_coupon_palette() -> MaterialPalette:
    """Return the coupon material palette (background, transparent, white, black)."""
    return MaterialPalette.from_sequence(
        (
            MaterialDefinition(0, "background", MaterialRole.BACKGROUND),
            MaterialDefinition(1, "transparent", MaterialRole.MATERIAL),
            MaterialDefinition(2, "white", MaterialRole.MATERIAL),
            MaterialDefinition(3, "black", MaterialRole.MATERIAL),
        )
    )


def window_coupon_payload_bytes() -> bytes:
    """Return the exact ``.npy`` bytes of the coupon payload."""
    buffer = io.BytesIO()
    np.save(buffer, window_coupon_label())
    return buffer.getvalue()


def window_coupon_manifest(payload_sha256: str) -> dict[str, Any]:
    """Return the ``vbdmat.voxels/1.0.0`` manifest document for the coupon."""
    tx, ty, tz = _COUPON_TRANSLATION_M
    return {
        "format": "vbdmat.voxels",
        "format_version": "1.0.0",
        "asset_type": "material-label",
        "payload": {
            "path": COUPON_PAYLOAD_NAME,
            "sha256": payload_sha256,
            "dtype": "uint16",
            "dimensions": ["z", "y", "x"],
        },
        "shape_zyx": list(_COUPON_SHAPE_ZYX),
        "voxel_size_xyz_m": list(_COUPON_VOXEL_SIZE_XYZ_M),
        "local_to_world": [
            [1, 0, 0, tx],
            [0, 1, 0, ty],
            [0, 0, 1, tz],
            [0, 0, 0, 1],
        ],
        "materials": [
            {"material_id": 0, "name": "background", "role": "background"},
            {"material_id": 1, "name": "transparent", "role": "material"},
            {"material_id": 2, "name": "white", "role": "material"},
            {"material_id": 3, "name": "black", "role": "material"},
        ],
        "source": {
            "generator": PHASE1_FIXTURE_GENERATOR,
            "generator_version": PHASE1_FIXTURE_GENERATOR_VERSION,
            "identity": "window-coupon",
            "notes": (
                "Phase 1 multi-material window coupon; transparent matrix with an "
                "asymmetric white inclusion and black marker. Research fixture, "
                "not a printer-vendor format."
            ),
        },
    }


def window_coupon_summary() -> CouponSummary:
    """Return the analytic coupon summary (derived from the definition, not readers)."""
    white = BoxRegion(2, *_COUPON_WHITE_ZYX)
    black = BoxRegion(3, *_COUPON_BLACK_ZYX)
    nz, ny, nx = _COUPON_SHAPE_ZYX
    total = nz * ny * nx
    counts = {
        0: 0,
        1: total - white.cell_count - black.cell_count,
        2: white.cell_count,
        3: black.cell_count,
    }
    sx, sy, sz = _COUPON_VOXEL_SIZE_XYZ_M
    tx, ty, tz = _COUPON_TRANSLATION_M
    bounds_max = (tx + nx * sx, ty + ny * sy, tz + nz * sz)
    return CouponSummary(
        shape_zyx=_COUPON_SHAPE_ZYX,
        voxel_size_xyz_m=_COUPON_VOXEL_SIZE_XYZ_M,
        local_to_world_translation_m=_COUPON_TRANSLATION_M,
        material_counts=counts,
        white_inclusion=white,
        black_marker=black,
        bounds_min_xyz_m=_COUPON_TRANSLATION_M,
        bounds_max_xyz_m=bounds_max,
        payload_sha256=hashlib.sha256(window_coupon_payload_bytes()).hexdigest(),
    )


# --------------------------------------------------------------------------- #
# Single-material stepped wedge (mesh path)
# --------------------------------------------------------------------------- #

_WEDGE_STEPS = 4
_WEDGE_RUN_MM = 4.0  # step run along +X
_WEDGE_RISE_MM = 2.0  # step rise along +Z
_WEDGE_DEPTH_MM = 6.0  # extrusion depth along +Y
_WEDGE_APEX_INDEX = 1  # profile vertex (N*run, 0), a kernel point of the region

WEDGE_MESH_NAME = "stepped_wedge.stl"


@dataclass(frozen=True, slots=True)
class WedgeSummary:
    """Analytic expectations for the stepped-wedge voxelization at 1 mm voxels."""

    source_unit: str
    voxel_size_xyz_m: tuple[float, float, float]
    material_id: int
    triangle_count: int
    bounds_min_xyz_m: tuple[float, float, float]
    bounds_max_xyz_m: tuple[float, float, float]
    shape_zyx: tuple[int, int, int]
    occupied_cells: int
    per_step_occupied: dict[int, int]


def _wedge_profile_xz() -> list[tuple[float, float]]:
    """Return the closed staircase profile in the X-Z plane (units applied later)."""
    n = _WEDGE_STEPS
    run = _WEDGE_RUN_MM
    rise = _WEDGE_RISE_MM
    profile: list[tuple[float, float]] = [
        (0.0, 0.0),
        (n * run, 0.0),
        (n * run, n * rise),
    ]
    for k in range(n, 0, -1):
        profile.append(((k - 1) * run, k * rise))
        if k > 1:
            profile.append(((k - 1) * run, (k - 1) * rise))
    return profile


def stepped_wedge_triangles() -> list[tuple[
    tuple[float, float, float],
    tuple[float, float, float],
    tuple[float, float, float],
]]:
    """Return the watertight stepped-wedge triangles in millimetres.

    The solid is the staircase profile extruded along +Y. Walls follow the profile
    order; the two caps fan from a kernel vertex with the opposite winding, so every
    shared edge is traversed once in each direction (a single, consistently oriented,
    2-manifold solid).
    """
    profile = _wedge_profile_xz()
    depth = _WEDGE_DEPTH_MM
    apex = _WEDGE_APEX_INDEX
    n = len(profile)
    front = [(x, 0.0, z) for (x, z) in profile]
    back = [(x, depth, z) for (x, z) in profile]

    triangles: list[tuple[
        tuple[float, float, float],
        tuple[float, float, float],
        tuple[float, float, float],
    ]] = []
    for i in range(n):
        j = (i + 1) % n
        triangles.append((front[i], front[j], back[j]))
        triangles.append((front[i], back[j], back[i]))
    for i in range(n):
        j = (i + 1) % n
        if i == apex or j == apex:
            continue
        triangles.append((front[apex], front[j], front[i]))  # y=0 cap, reversed
        triangles.append((back[apex], back[i], back[j]))  # y=depth cap
    return triangles


def stepped_wedge_stl_bytes() -> bytes:
    """Return a deterministic ASCII STL of the stepped wedge (units: millimetres)."""
    lines = ["solid stepped_wedge"]
    for a, b, c in stepped_wedge_triangles():
        lines.append("facet normal 0 0 0")
        lines.append("outer loop")
        for vertex in (a, b, c):
            lines.append(
                f"vertex {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}"
            )
        lines.append("endloop")
        lines.append("endfacet")
    lines.append("endsolid stepped_wedge")
    return ("\n".join(lines) + "\n").encode("ascii")


def stepped_wedge_summary() -> WedgeSummary:
    """Return analytic wedge expectations at 1 mm isotropic voxels with padding 1."""
    n = _WEDGE_STEPS
    run_cells = int(_WEDGE_RUN_MM)  # 1 mm voxels
    rise_cells = int(_WEDGE_RISE_MM)
    depth_cells = int(_WEDGE_DEPTH_MM)
    # Step k spans a run of cells, height (rise * k) cells, depth cells.
    per_step = {
        k: run_cells * depth_cells * (rise_cells * k) for k in range(1, n + 1)
    }
    occupied = sum(per_step.values())
    # Padding of one cell each side: interior 16x6x8 mm grid becomes 18x8x10.
    shape_x = n * run_cells + 2
    shape_y = depth_cells + 2
    shape_z = n * rise_cells + 2
    return WedgeSummary(
        source_unit="mm",
        voxel_size_xyz_m=(0.001, 0.001, 0.001),
        material_id=1,
        triangle_count=len(stepped_wedge_triangles()),
        bounds_min_xyz_m=(0.0, 0.0, 0.0),
        bounds_max_xyz_m=(
            n * _WEDGE_RUN_MM / 1000.0,
            _WEDGE_DEPTH_MM / 1000.0,
            n * _WEDGE_RISE_MM / 1000.0,
        ),
        shape_zyx=(shape_z, shape_y, shape_x),
        occupied_cells=occupied,
        per_step_occupied=per_step,
    )


# --------------------------------------------------------------------------- #
# Materialization
# --------------------------------------------------------------------------- #


def _summary_json(summary: CouponSummary | WedgeSummary) -> str:
    def _default(obj: Any) -> Any:
        if isinstance(obj, BoxRegion):
            return {
                "material_id": obj.material_id,
                "z": list(obj.z),
                "y": list(obj.y),
                "x": list(obj.x),
                "cell_count": obj.cell_count,
            }
        raise TypeError(f"cannot serialize {type(obj)!r}")

    payload = {key: getattr(summary, key) for key in summary.__slots__}
    # dict keys with int material IDs must become strings in JSON.
    for key, value in list(payload.items()):
        if isinstance(value, dict):
            payload[key] = {str(k): v for k, v in value.items()}
        elif isinstance(value, tuple):
            payload[key] = list(value)
    return json.dumps(payload, indent=2, sort_keys=True, default=_default) + "\n"


def write_phase1_fixtures(directory: str | Path) -> dict[str, Path]:
    """Write all Phase 1 fixtures and expected summaries under ``directory``.

    Returns a mapping of logical name to the written path. Regeneration is
    byte-identical: payloads and meshes come from deterministic pure functions.
    """
    base = Path(directory)
    base.mkdir(parents=True, exist_ok=True)

    payload = window_coupon_payload_bytes()
    sha = hashlib.sha256(payload).hexdigest()
    written: dict[str, Path] = {}

    payload_path = base / COUPON_PAYLOAD_NAME
    payload_path.write_bytes(payload)
    written["coupon_payload"] = payload_path

    manifest_path = base / COUPON_MANIFEST_NAME
    manifest_path.write_text(
        json.dumps(window_coupon_manifest(sha), indent=2) + "\n", encoding="utf-8"
    )
    written["coupon_manifest"] = manifest_path

    coupon_summary_path = base / "window_coupon.expected.json"
    coupon_summary_path.write_text(
        _summary_json(window_coupon_summary()), encoding="utf-8"
    )
    written["coupon_summary"] = coupon_summary_path

    mesh_path = base / WEDGE_MESH_NAME
    mesh_path.write_bytes(stepped_wedge_stl_bytes())
    written["wedge_mesh"] = mesh_path

    wedge_summary_path = base / "stepped_wedge.expected.json"
    wedge_summary_path.write_text(
        _summary_json(stepped_wedge_summary()), encoding="utf-8"
    )
    written["wedge_summary"] = wedge_summary_path

    return written
