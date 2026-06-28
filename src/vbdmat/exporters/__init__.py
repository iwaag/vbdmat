"""Optional renderer adapters and shared capability diagnostics."""

from .diagnostics import CapabilityEntry, CapabilityReport
from .mitsuba import (
    DEFAULT_MITSUBA_CONFIG,
    MITSUBA_ADAPTER,
    MITSUBA_ADAPTER_VERSION,
    MitsubaExportConfig,
    MitsubaExportError,
    MitsubaFieldConversion,
    MitsubaRenderResult,
    PreparedMitsubaScene,
    convert_optical_fields,
    mitsuba_capability_report,
    prepare_mitsuba_scene,
    render_mitsuba,
)

__all__ = [
    "DEFAULT_MITSUBA_CONFIG",
    "MITSUBA_ADAPTER",
    "MITSUBA_ADAPTER_VERSION",
    "CapabilityEntry",
    "CapabilityReport",
    "MitsubaExportConfig",
    "MitsubaExportError",
    "MitsubaFieldConversion",
    "MitsubaRenderResult",
    "PreparedMitsubaScene",
    "convert_optical_fields",
    "mitsuba_capability_report",
    "prepare_mitsuba_scene",
    "render_mitsuba",
]
