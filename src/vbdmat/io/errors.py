"""Errors raised while reading and writing persisted volume assets."""


class VolumeIOError(ValueError):
    """A persistent asset violates the Zarr layout or compatibility contract."""

    def __init__(self, field_path: str, message: str) -> None:
        self.field_path = field_path
        self.message = message
        super().__init__(f"{field_path}: {message}")
