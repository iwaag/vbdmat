"""Deterministic canonical fixtures for tests and technical proofs."""

from .synthetic import (
    FIXTURE_GENERATOR,
    FIXTURE_GENERATOR_VERSION,
    SYNTHETIC_FIXTURE_FACTORIES,
    FixtureManifest,
    SelectedCellExpectation,
    SyntheticFixture,
    all_synthetic_fixtures,
    anisotropic_axis_marker,
    homogeneous_scattering_white,
    homogeneous_transparent,
    layered_material_slab,
    transparent_opaque_interface,
    two_material_mixture_ramp,
)

__all__ = [
    "FIXTURE_GENERATOR",
    "FIXTURE_GENERATOR_VERSION",
    "SYNTHETIC_FIXTURE_FACTORIES",
    "FixtureManifest",
    "SelectedCellExpectation",
    "SyntheticFixture",
    "all_synthetic_fixtures",
    "anisotropic_axis_marker",
    "homogeneous_scattering_white",
    "homogeneous_transparent",
    "layered_material_slab",
    "transparent_opaque_interface",
    "two_material_mixture_ramp",
]
