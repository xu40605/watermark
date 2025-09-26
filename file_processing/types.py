from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


class NamingMode(str, Enum):
    KEEP = "keep"
    PREFIX = "prefix"
    SUFFIX = "suffix"


class ResizeMode(str, Enum):
    NONE = "none"
    BY_WIDTH = "by_width"
    BY_HEIGHT = "by_height"
    BY_PERCENT = "by_percent"


@dataclass(frozen=True)
class ExportOptions:
    """Options controlling export behavior.

    - output_dir: Target directory. Must not equal any source directory unless allow_overwrite_source=True
    - output_format: "jpeg" or "png"
    - naming_mode: How to transform filenames
    - prefix/suffix: Used when naming_mode is PREFIX or SUFFIX
    - jpeg_quality: 0-100 for JPEG; ignored for PNG
    - resize_mode: How to resize images; NONE leaves as-is
    - resize_value: int value for width/height or percent depending on resize_mode
    - keep_aspect_ratio: Maintain original aspect when resizing by one dimension
    """

    output_dir: Path
    output_format: str = "jpeg"
    naming_mode: NamingMode = NamingMode.KEEP
    prefix: str = ""
    suffix: str = ""
    jpeg_quality: int = 90
    resize_mode: ResizeMode = ResizeMode.NONE
    resize_value: Optional[int] = None
    keep_aspect_ratio: bool = True
    allow_overwrite_source: bool = False


@dataclass(frozen=True)
class ImportResult:
    """Represents discovered input files and their common root directory."""

    files: List[Path]
    common_root: Path


