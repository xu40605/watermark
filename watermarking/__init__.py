"""Watermarking package for applying visual watermarks to images.

Current scope (per PRD core requirements):
- Text watermark with configurable content, font size, color, opacity
- Positioning via nine-grid presets with safe margins and bounds checks

Modules:
- types: shared enums and option dataclasses
- positioning: compute pixel coordinates from presets
- text_renderer: render text onto images with opacity
"""

from .types import GridPosition, TextWatermarkOptions
from .positioning import compute_position
from .text_renderer import apply_text_watermark

__all__ = [
    "GridPosition",
    "TextWatermarkOptions",
    "compute_position",
    "apply_text_watermark",
]


