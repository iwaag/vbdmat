"""Shared restored-Zarr export boundary tests."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from vbdmat.exporters import ExportInputError, export_restored_optical
from vbdmat.fixtures import anisotropic_axis_marker
from vbdmat.io import write_volume
from vbdmat.optics import map_material_volume_to_optical, phase0_provisional_mapping


class _Transform:
    def copy(self) -> _Transform:
        return self


class _Grid:
    def __init__(self) -> None:
        self.metadata: dict[str, str] = {}

    def __setitem__(self, key: str, value: str) -> None:
        self.metadata[key] = value

    def copyFromArray(self, array: np.ndarray, tolerance: float) -> None:
        assert array.ndim == 3
        assert tolerance == 0.0


def test_openvdb_export_restores_zarr_and_returns_complete_diagnostics(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def write(path: str, *, grids: object, metadata: object) -> None:
        assert grids
        assert metadata
        Path(path).write_bytes(b"fake-vdb")

    fake = SimpleNamespace(
        __version__="test-openvdb",
        FloatGrid=_Grid,
        createLinearTransform=lambda *, matrix: _Transform(),
        write=write,
    )
    monkeypatch.setitem(sys.modules, "openvdb", fake)
    fixture = anisotropic_axis_marker()
    optical = map_material_volume_to_optical(
        fixture.volume, phase0_provisional_mapping()
    )
    source = tmp_path / "optical.zarr"
    output = tmp_path / "export"
    write_volume(source, optical)

    outcome = export_restored_optical("openvdb", source, output)
    document = outcome.to_dict()

    assert document["adapter"] == "vbdmat.exporters.openvdb"
    assert document["renderer"] == {
        "name": "openvdb",
        "version": "test-openvdb",
    }
    assert {entry["field"] for entry in document["capabilities"]["entries"]} >= {
        "geometry",
        "sigma_a",
        "sigma_s",
        "g",
        "ior",
    }
    assert set(document["artifacts"]) == {
        "capabilities.json",
        "openvdb-manifest.json",
        "volume.vdb",
    }


def test_export_rejects_non_optical_zarr_before_loading_adapter(
    tmp_path: Path,
) -> None:
    source = tmp_path / "material.zarr"
    write_volume(source, anisotropic_axis_marker().volume)

    with pytest.raises(ExportInputError, match="optical-property"):
        export_restored_optical("openvdb", source, tmp_path / "export")
