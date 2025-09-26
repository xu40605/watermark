from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Tuple


class GridPosition(str, Enum):
    """Nine-grid preset layout for watermark placement."""

    TOP_LEFT = "top_left"
    TOP_CENTER = "top_center"
    TOP_RIGHT = "top_right"
    CENTER_LEFT = "center_left"
    CENTER = "center"
    CENTER_RIGHT = "center_right"
    BOTTOM_LEFT = "bottom_left"
    BOTTOM_CENTER = "bottom_center"
    BOTTOM_RIGHT = "bottom_right"


@dataclass(frozen=True)
class TextWatermarkOptions:
    """Options to control text watermark rendering.

    - text: watermark content
    - font_size: integer pixel size
    - color: RGB tuple (0-255)
    - opacity: 0-100 percentage
    - position: nine-grid preset
    - margin: padding from the image edges (pixels)
    """

    text: str
    font_size: int = 24
    color: Tuple[int, int, int] = (255, 255, 255)
    opacity: int = 100
    position: GridPosition = GridPosition.BOTTOM_RIGHT
    margin: int = 20


