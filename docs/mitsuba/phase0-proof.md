# Phase 0 Mitsuba 3 Consumer Proof

**Date:** 2026-06-28  
**Mitsuba:** 3.9.0  
**Variant:** `llvm_ad_rgb`  
**Reference render:** 64 × 64, 32 spp, seed 20260628, `volpath` depth 8

## Reproduction

```bash
uv sync --locked --group mitsuba
uv run --group mitsuba python examples/phase0/render_mitsuba_fixtures.py \
  .local/phase0/mitsuba-step9
```

Each fixture directory contains:

- linear RGB EXR and display PNG;
- a fixed-gain attenuation diagnostic PNG;
- complete exterior containment and internal IOR-interface PLY meshes;
- `capabilities.json`;
- `scene-summary.json`.

The output root contains `render-report.json` with paths, hashes, extrema, and linear RGB
means.

## Mapping

| Canonical semantic | Mitsuba mapping | Disposition |
| --- | --- | --- |
| Geometry | ZYX tensor plus metric `to_world`; world PLY vertices | Transformed |
| `m^-1` units | Scene metres, medium scale 1 | Represented |
| RGB basis | Raw three-channel RGB transport tensor | Approximated |
| `sigma_a`, `sigma_s` | `sigma_t = sigma_a + sigma_s`; `albedo = sigma_s / sigma_t` | Transformed |
| `g` | Global scattering-weighted HG scalar | Approximated |
| Spatial `ior` | Not accepted by heterogeneous medium | Unsupported |
| Derived IOR interfaces | Oriented dielectric PLY patches | Transformed |

Both grids use nearest filtering. Exterior patches delimit the medium even when their
IOR is index matched. Internal dielectric patches retain the same heterogeneous medium
on both sides while changing refraction according to the two cell values.

## Reference hashes

| Fixture | Display PNG SHA-256 | Attenuation PNG SHA-256 | Mean linear RGB |
| --- | --- | --- | --- |
| homogeneous-transparent | `3436eabe928df2adec6b4d54d1764cc24d074b22865d9583296844145a028f90` | `288a9473182a17d7ee301ad4015e81c0900f9315e4ca9721862b666ef0449320` | `(0.897956, 0.897965, 0.897970)` |
| homogeneous-scattering-white | `534ad7b3ea877a9be685b7ecc34e1dad159b072f3636523688c31bd5bdf3cbf9` | `9e122be1eeb6296e8df699f315dd1a8d2791492fb44c1aed017adb6212e01ec4` | `(0.894781, 0.894781, 0.894781)` |
| transparent-opaque-interface | `1e999e5d22d33018cb5459882240397b72042ffdb23712176c80af7ebc5f1ef6` | `a433fa666c40556829e91493cb0f5b6f31a9905378e6af14e3b7f562f91703cf` | `(0.896701, 0.896060, 0.895449)` |
| layered-material-slab | `cdaa81a3d6fcbdfcf8697763f6d6ca2f88ab8b2cf09c90d9a43de3df062c7e90` | `b1804c88b4665325b99f0ee91a3c15f984b151bf2380afc56e3606507d77348d` | `(0.895400, 0.894512, 0.893668)` |
| two-material-mixture-ramp | `107afd1fe687b01afbc94a6cc7c7ac578f616ab63578fed280ec699ceb62ecb4` | `3e1042878092a637e4b4852801c284e47ec722a53986cbc7efb2365441f7b831` | `(0.900689, 0.900690, 0.900690)` |
| anisotropic-axis-marker | `7d958bc7a4494bfc110ce5a411983fe0189079b49b0034e1d74604399548347d` | `cd5da12a208cd5a917f0fd72561b4c5ecd7570c9816138a1c0101d6c311f5059` | `(0.999901, 0.999901, 0.999947)` |

Hashes cover PNG bytes. EXR remains the authoritative linear render. The diagnostic PNG
is a fixed display transform and may amplify Monte Carlo or mesh-edge errors as well as
real attenuation.

## Orientation and scale evidence

Automated checks establish the consumer contract before rendering:

- tensor shape is exactly `(z, y, x, 3)`;
- selected X/Y/Z marker cells retain their distinct coefficient triplets;
- the volume transform maps the unit grid domain to canonical translated, anisotropic
  metric bounds;
- internal interface PLY coordinates use the same world transform;
- every fixture scene loads and renders without edits.

This is stronger than inferring orientation from a tiny image alone. The angled fixed
camera and attenuation diagnostic remain gross visual regression aids.

## Qualitative response check

Under the fixed backlight, homogeneous test volumes were rendered with coefficients
`0`, `10,000`, and `50,000 m^-1`. Mean image radiance decreased strictly for both tests:

| Changed field | Means from low to high coefficient |
| --- | --- |
| `sigma_a` | `1.000000 > 0.967231 > 0.926649` (approximately; fixed test scene) |
| `sigma_s` | `1.000000 > 0.967703 > 0.927618` (approximately; fixed test scene) |

The automated assertion checks ordering rather than these rounded example values.

## Known limitations

- Spatial `g` is reduced to one scattering-weighted scalar.
- Effective RGB transport is not a spectral interpretation.
- Unit-cell boundary patches are not merged and can create coincident-edge artifacts.
- Complex nested dielectric correctness remains a proof approximation.
- Reference coefficients are provisional and uncalibrated.
- Images are regression/sanity artifacts, not cross-renderer physical ground truth.

