"""Package installation smoke tests."""

from pathlib import Path

import vbdmat


def test_package_imports_from_installed_source_tree() -> None:
    """The test must exercise uv's editable package installation."""
    package_file = Path(vbdmat.__file__).resolve()

    assert package_file.parts[-3:] == ("src", "vbdmat", "__init__.py")
    assert vbdmat.__version__ == "0.1.0"
