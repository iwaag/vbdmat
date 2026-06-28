# VBDMAT

VBDMAT is a renderer-independent preprocessing backend for voxel-based
material-jetting appearance research. The project will convert material voxel
data into explicit optical-property volumes for downstream renderers.

The repository is currently in Phase 0. This phase establishes volume schemas,
physical conventions, persistence, and renderer interoperability proofs. It
does not yet provide calibrated appearance prediction or production CAD
voxelization.

## Requirements

- [uv](https://docs.astral.sh/uv/)

uv manages the Python installation, virtual environment, dependencies,
lockfile, and project commands. No separate `pip`, Poetry, or Conda workflow is
supported.

## Development setup

Install the Python version selected by the repository and synchronize the
locked default environment:

```bash
uv python install
uv sync --locked
```

Run all checks through uv:

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy src
uv run pytest
```

Use `uv add <package>` for runtime dependencies and
`uv add --group dev <package>` for development-only dependencies. Commit both
`pyproject.toml` and `uv.lock` when dependencies change.

## Optional integration environments

Renderer proofs are kept out of the default environment:

```bash
uv sync --locked --group mitsuba
uv sync --locked --group openvdb
```

The OpenVDB group is initially empty because compatible Python bindings may be
provided by the host DCC or system installation. Phase 0 will document the
selected integration environment before that proof is implemented.

## Current package

The package currently exposes the Phase 0 core foundation:

```text
src/vbdmat/
  core/
    axes.py
    errors.py
    geometry.py
    materials.py
    metadata.py
    optical_basis.py
    transforms.py
    validation.py
    volumes.py
  fixtures/
    synthetic.py
  optics/
    config.py
    mapping.py
  io/
    zarr.py
  boundaries/
    interfaces.py
    policies.py
  exporters/
    diagnostics.py
    mitsuba.py
tests/
```

The public core API includes `GridGeometry`, `OpticalBasis`, material palette
types, schema and provenance metadata, `MaterialLabelVolume`,
`MaterialMixtureVolume`, `OpticalPropertyVolume`, and structured volume
validation errors. Zarr v3 persistence supports failure-safe writes, validated
full reads, metadata-only inspection, and spatial optical-field reads. Renderer
I/O remains intentionally unimplemented until its Phase 0 steps.

Generate and inspect the small deterministic Phase 0 fixtures with:

```bash
uv run python examples/phase0/inspect_synthetic_fixtures.py
```

The fixture set covers homogeneous transparent and white commands, a sharp
transparent/opaque interface, a layered slab, a two-material mixture ramp, and
an anisotropic axis marker.

Apply the explicit provisional and uncalibrated Phase 0 optical mapping with:

```bash
uv run python examples/phase0/map_synthetic_fixtures.py
```

The reference mapping uses direct label lookup and linear volume-fraction
mixing. Its assumptions and provisional values are documented in
[Phase 0 Reference Optical Mapping v1](docs/optics/reference-mapping-v1.md).

Inspect a persisted volume without loading array payloads, or generate the
fixture size and partial-read report:

```bash
uv run python examples/phase0/inspect_zarr.py path/to/asset.zarr
uv run python examples/phase0/zarr_fixture_report.py
```

Derive and inspect sharp refractive-index interfaces from every mapped fixture:

```bash
uv run python examples/phase0/inspect_ior_interfaces.py
```

Reproduce the optional Mitsuba IOR API probe with the locked renderer group:

```bash
uv run --group mitsuba python examples/phase0/probe_mitsuba_ior.py
```

The probe confirms that heterogeneous-medium spatial IOR is rejected while scalar
dielectric `int_ior`/`ext_ior` is accepted.

Render all canonical fixture proofs with fixed Mitsuba settings:

```bash
uv run --group mitsuba python examples/phase0/render_mitsuba_fixtures.py \
  .local/phase0/mitsuba-step9
```

Each fixture directory contains EXR/PNG output, oriented boundary PLY files, a scene
summary, and a machine-readable capability report.

## Phase 0 design contracts

- [ADR-001: coordinates, axes, units, and sampling](docs/adr/0001-coordinates-axes-units-and-sampling.md)
- [ADR-002: canonical volume schemas](docs/adr/0002-canonical-volume-schemas.md)
- [ADR-003: boundaries and refractive index](docs/adr/0003-boundaries-and-refractive-index.md)
- [ADR-004: Zarr layout and compatibility](docs/adr/0004-zarr-layout-and-compatibility.md)
- [ADR-005: exporter boundary](docs/adr/0005-exporter-boundary.md)
- [Logical volume schema 1.0](docs/schemas/volume-schema-v1.md)
- [Worked schema examples](docs/schemas/examples/)
- [Phase 0 Zarr fixture report](docs/zarr/phase0-fixture-report.md)
- [Phase 0 Mitsuba consumer proof](docs/mitsuba/phase0-proof.md)

## License

The repository is dedicated to the public domain under CC0 1.0 Universal. See
`LICENSE`.
