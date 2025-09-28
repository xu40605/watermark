"""Watermarking package for applying visual watermarks to images.

Current scope (per PRD core requirements):
- Text watermark with configurable content, font selection, font size, color, opacity
- Positioning via nine-grid presets with safe margins and bounds checks
- Watermark layout and style customization

Modules:
- types: shared enums and option dataclasses
- positioning: compute pixel coordinates from presets and validate positions
- text_renderer: render text onto images with style customization
"""

from .types import GridPosition, TextWatermarkOptions
from .positioning import compute_position, validate_position_within_bounds, get_position_name
from .text_renderer import apply_text_watermark, get_text_dimensions, is_font_available

__all__ = [
    "GridPosition",
    "TextWatermarkOptions",
    "compute_position",
    "validate_position_within_bounds",
    "get_position_name",
    "apply_text_watermark",
    "get_text_dimensions",
    "is_font_available",
]


