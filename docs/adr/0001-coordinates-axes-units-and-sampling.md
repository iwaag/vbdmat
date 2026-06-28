# ADR-001: Coordinates, Axes, Units, and Sampling

- **Status:** Accepted
- **Date:** 2026-06-28
- **Decision owners:** VBDMAT maintainers
- **Phase:** 0, Step 2

## Context

VBDMAT moves voxel data between array libraries, persistent stores, geometry tools, and renderers. Those systems do not share one axis order, up axis, length unit, or sampling convention. An implicit transpose, half-voxel translation, or millimetre/metre mismatch can produce plausible but invalid output.

The canonical convention must support anisotropic printer voxels, arbitrary rigid placement in a scene, spatial subsetting, and deterministic conversion between array indices and world coordinates. It must remain independent of any one renderer.

## Decision

### World coordinate system

The canonical world space is right-handed and uses metres:

- `+X` and `+Y` span the nominal printer build plane;
- `+Z` is the nominal build direction and world up direction;
- `X cross Y = Z`;
- distances and translations are expressed in metres.

A volume may be rigidly rotated and translated away from the nominal print orientation. Print orientation is therefore metadata or provenance, not an excuse to reinterpret array axes.

### Semantic axes and array storage order

Semantic spatial coordinates are always written `(x, y, z)`. NumPy spatial dimensions are always stored in `(z, y, x)` order.

- A scalar field has shape `(nz, ny, nx)`.
- A basis-valued field has shape `(nz, ny, nx, nbasis)`.
- A material-mixture field has shape `(nz, ny, nx, nmaterial)`.
- An element is indexed as `array[z, y, x]` or `array[z, y, x, component]`.

Dimension names are stored explicitly. Consumers must use the declared dimension names and must not infer them only from shape.

### Grid geometry

Canonical grid geometry contains:

- `shape_zyx = (nz, ny, nx)`, with every extent greater than zero;
- `voxel_size_xyz_m = (sx, sy, sz)`, with every size finite and greater than zero;
- `local_to_world`, a finite `4 x 4` homogeneous rigid transform stored as row-major numbers.

Local metric coordinates are measured in metres. The upper-left `3 x 3` block of `local_to_world` must be an orthonormal rotation with determinant `+1`. Reflection, scale, shear, and perspective are forbidden. Its last row must be `[0, 0, 0, 1]`. Translation is stored in the last column and is measured in metres.

Voxel scale is represented only by `voxel_size_xyz_m`, not duplicated in the transform. The transform translation is the world position of the minimum local grid corner. There is no separate canonical `origin` field.

### Sampling location

Voxel values are cell-centred and piecewise constant in the canonical representation. Integer indices identify cells, not sample points at cell corners.

For array index `(z, y, x)`, define the continuous XYZ index coordinate of its centre as:

```text
c_index = (x + 0.5, y + 0.5, z + 0.5)
```

The local metric centre is:

```text
c_local = (
    sx * (x + 0.5),
    sy * (y + 0.5),
    sz * (z + 0.5),
)
```

The world centre is:

```text
c_world_h = local_to_world @ (c_local.x, c_local.y, c_local.z, 1)
```

The minimum grid corner is local `(0, 0, 0)`. The maximum grid corner is local `(nx*sx, ny*sy, nz*sz)`.

### Bounds and containment

Grid bounds are half-open in continuous index space:

```text
[0, nx) x [0, ny) x [0, nz)
```

An internal boundary plane at integer coordinate `k` belongs to cell `k`; the maximum plane at an extent is outside the grid. Conversion from a contained continuous index coordinate to a cell index uses `floor` per semantic XYZ axis and then returns array order `(z, y, x)`.

Floating-point callers must use the common geometry helpers planned for Step 3 instead of adding private epsilon rules. Geometry helpers will expose explicit containment and clamping operations; conversion will not silently clamp out-of-bounds positions.

### Index-to-world conversion

For a continuous XYZ index coordinate `q_index = (qx, qy, qz)` measured from the minimum corner:

```text
q_local = (sx*qx, sy*qy, sz*qz)
q_world_h = local_to_world @ (q_local.x, q_local.y, q_local.z, 1)
```

World-to-index conversion applies `inverse(local_to_world)` and divides the resulting local XYZ coordinate by `(sx, sy, sz)`. APIs must state whether they accept a continuous corner-relative coordinate or an integer cell index.

### Numeric representation and tolerances

- Geometry metadata and transform calculations use IEEE-754 `float64`.
- Array coefficient dtypes are decided separately in ADR-002.
- Stored inputs must be finite.
- Transform validation uses absolute tolerance `1e-9` for the last row, orthonormality, and determinant checks.
- Index/world round-trip tests use absolute tolerance `1e-9` in continuous index units for the small Phase 0 fixtures.
- These tolerances are validation and test contracts, not permission to snap or mutate user data.

## Worked Example: Anisotropic `4 x 3 x 2` Volume

The example has four X cells, three Y cells, and two Z cells:

```text
shape_zyx = (2, 3, 4)
voxel_size_xyz_m = (0.00004, 0.00005, 0.00003)
```

Its local physical extent is:

```text
(nx*sx, ny*sy, nz*sz)
= (4*0.00004, 3*0.00005, 2*0.00003)
= (0.00016, 0.00015, 0.00006) metres
```

Use a translation-only transform:

```text
local_to_world =
[[1, 0, 0, 0.010],
 [0, 1, 0, 0.020],
 [0, 0, 1, 0.030],
 [0, 0, 0, 1    ]]
```

For array element `array[1, 2, 3]`, the semantic cell index is `(x=3, y=2, z=1)`. Its continuous index centre is `(3.5, 2.5, 1.5)`, its local metric centre is:

```text
(3.5*0.00004, 2.5*0.00005, 1.5*0.00003)
= (0.00014, 0.000125, 0.000045) metres
```

and its world centre is:

```text
(0.01014, 0.020125, 0.030045) metres
```

The valid integer array indices are `z=0..1`, `y=0..2`, and `x=0..3`. The point at continuous index `(4, 3, 2)` lies on the excluded maximum boundary.

## Rejected Alternatives

### Store arrays in `(x, y, z)` order

Rejected because NumPy and volume-processing code conventionally benefit from X being the fastest-varying spatial axis. Explicit dimension metadata prevents relying on convention alone.

### Encode voxel size in the affine transform

Rejected because it makes anisotropic voxel dimensions harder to inspect and invites scale to be represented twice. A rigid placement transform plus explicit voxel size has one meaning.

### Use millimetres as the canonical unit

Rejected because optical transport coefficients are conventionally inverse length and downstream scientific tools commonly use SI. User-facing APIs may accept millimetres but must convert at the boundary.

### Sample at voxel corners

Rejected because material and optical values represent finite cells. Corner sampling would leave interface ownership and volume bounds ambiguous.

### Permit general affine transforms

Rejected for Phase 0 because shear and non-uniform transform scale alter voxel geometry and coefficient interpretation. Such transforms must be resampled into a canonical grid rather than attached as metadata.

## Consequences

- Storage order and physical axis order are deliberately different and must be handled by shared helpers.
- Renderer adapters must convert metres or up-axis conventions explicitly and report that conversion.
- Spatial subsets retain voxel size and rotation but update transform translation to the subset's minimum local corner.
- Reflections and shears require resampling before creating a canonical volume.
- Step 3 can implement geometry types without unresolved origin, sampling, or transform semantics.

## Compliance Checks for Step 3

- Reject zero or negative extents and voxel sizes.
- Reject non-finite geometry values.
- Reject transforms that are not rigid and right-handed.
- Test the worked example exactly.
- Test rotated and translated grids.
- Test half-open maximum bounds and internal boundary ownership.
- Test index-to-world-to-index round trips at centres and corners.
