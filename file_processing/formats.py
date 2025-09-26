from __future__ import annotations

from pathlib import Path
from typing import Set

# Input formats (must support transparency for PNG)
SUPPORTED_INPUT_EXTS: Set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"}

# Output formats user can choose
SUPPORTED_OUTPUT_EXTS: Set[str] = {"jpeg", "png"}


def is_supported_input(path: Path) -> bool:
    """Return True if the file has a supported image extension."""
    return path.suffix.lower() in SUPPORTED_INPUT_EXTS


