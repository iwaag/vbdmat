"""Regenerate the committed Phase 1 representative input fixtures.

Deterministic: rerunning this script reproduces byte-identical payloads, meshes, and
expected summaries under ``examples/phase1/inputs/``. Intentionally invalid samples for
error-path tests are written under ``examples/phase1/inputs/invalid/``.

Usage::

    uv run python examples/phase1/generate_fixtures.py
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from vbdmat.fixtures import (
    COUPON_PAYLOAD_NAME,
    stepped_wedge_stl_bytes,
    window_coupon_manifest,
    window_coupon_payload_bytes,
    write_phase1_fixtures,
)

INPUTS = Path(__file__).parent / "inputs"
INVALID = INPUTS / "invalid"


def _write_invalid_samples() -> None:
    INVALID.mkdir(parents=True, exist_ok=True)

    # 1. Direct-voxel manifest whose declared checksum does not match the payload.
    payload = window_coupon_payload_bytes()
    correct_sha = hashlib.sha256(payload).hexdigest()
    bad_manifest = window_coupon_manifest("0" * 64)
    bad_manifest["source"]["identity"] = "window-coupon-bad-checksum"
    (INVALID / COUPON_PAYLOAD_NAME).write_bytes(payload)
    (INVALID / "window_coupon.bad_checksum.voxels.json").write_text(
        json.dumps(bad_manifest, indent=2) + "\n", encoding="utf-8"
    )
    assert correct_sha != "0" * 64  # sanity: the sample really is inconsistent

    # 2. Open (non-watertight) mesh: the full wedge minus its final triangle.
    stl_lines = stepped_wedge_stl_bytes().decode("ascii").splitlines()
    end = stl_lines.pop()  # "endsolid stepped_wedge"
    # Drop the last facet (7 lines: facet/outer loop/3x vertex/endloop/endfacet).
    del stl_lines[-7:]
    stl_lines.append(end)
    (INVALID / "stepped_wedge.open.stl").write_text(
        "\n".join(stl_lines) + "\n", encoding="ascii"
    )


def main() -> None:
    written = write_phase1_fixtures(INPUTS)
    _write_invalid_samples()
    for name, path in written.items():
        print(f"{name}: {path.relative_to(INPUTS.parent)}")
    print("invalid samples written under", INVALID.relative_to(INPUTS.parent))


if __name__ == "__main__":
    main()
