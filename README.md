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

The initial package is deliberately minimal:

```text
src/vbdmat/
tests/
```

Architecture and implementation modules will be introduced only after their
Phase 0 contracts have been recorded as architecture decisions.

## License

The repository is dedicated to the public domain under CC0 1.0 Universal. See
`LICENSE`.
