"""Material-to-optical mapping configuration and reference conversion."""

from .config import (
    CalibrationStatus,
    MaterialOpticalProperties,
    MixingRule,
    OpticalMappingConfig,
    phase0_provisional_mapping,
)
from .errors import OpticalMappingError
from .mapping import (
    MAPPING_GENERATOR,
    MAPPING_GENERATOR_VERSION,
    map_material_volume_to_optical,
)

__all__ = [
    "MAPPING_GENERATOR",
    "MAPPING_GENERATOR_VERSION",
    "CalibrationStatus",
    "MaterialOpticalProperties",
    "MixingRule",
    "OpticalMappingConfig",
    "OpticalMappingError",
    "map_material_volume_to_optical",
    "phase0_provisional_mapping",
]
