from __future__ import annotations

from typing import Tuple, Optional
import os

from PIL import Image, ImageDraw, ImageFont

from .positioning import compute_position
from .types import GridPosition, TextWatermarkOptions


def _load_font(font_size: int, font_name: Optional[str] = None) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Attempt to load a system font; fallback to default.

    Args:
        font_size: Size of the font in pixels
        font_name: Name of the font to load (optional)

    Returns:
        Loaded font object
    """
    # List of common system font paths to try
    system_font_paths = [
        # Windows fonts
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/microsoftyahei.ttf",  # 微软雅黑
        # Common font names that PIL might find
        "Arial",
        "SimHei",
        "SimSun",
        "Microsoft YaHei",
    ]

    # First try the specified font name if provided
    if font_name:
        try:
            return ImageFont.truetype(font_name, font_size)
        except Exception:
            # If specified font fails, continue to try other options
            pass

    # Try system fonts
    for font_path in system_font_paths:
        try:
            return ImageFont.truetype(font_path, font_size)
        except Exception:
            continue

    # Fallback to default font
    return ImageFont.load_default()


def _clamp_opacity(opacity: int) -> int:
    """Clamp opacity value between 0 and 100.
    
    Args:
        opacity: Original opacity value
    
    Returns:
        Clamped opacity value
    """
    return max(0, min(100, int(opacity)))


def apply_text_watermark(
    image: Image.Image,
    options: TextWatermarkOptions,
) -> Image.Image:
    """Render a text watermark onto a copy of the provided image.

    - Respects opacity (0-100), color, font size
    - Places watermark using nine-grid presets with margins
    - Ensures result remains within bounds

    Args:
        image: Original image to apply watermark to
        options: Text watermark options

    Returns:
        New image with watermark applied
    """
    if options.opacity <= 0 or not options.text:
        return image.copy()

    # Work in RGBA to support alpha compositing
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Load font with specified font name
    font = _load_font(options.font_size, options.font_name)
    
    # Calculate text dimensions
    bbox = draw.textbbox((0, 0), options.text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Compute position using nine-grid layout
    x, y = compute_position(
        img_w=base.width,
        img_h=base.height,
        box_w=text_w,
        box_h=text_h,
        position=options.position,
        margin=options.margin,
    )

    # Compose color with alpha from opacity
    r, g, b = options.color
    alpha = int(255 * (_clamp_opacity(options.opacity) / 100.0))
    draw.text((x, y), options.text, font=font, fill=(r, g, b, alpha))

    # Composite overlay onto base
    result = Image.alpha_composite(base, overlay)
    return result.convert(image.mode)


def get_text_dimensions(text: str, font_size: int, font_name: Optional[str] = None) -> Tuple[int, int]:
    """Calculate the dimensions of a text string with given font settings.
    
    Args:
        text: Text to measure
        font_size: Font size in pixels
        font_name: Font name (optional)
    
    Returns:
        Tuple of (width, height) of the text in pixels
    """
    # Create a temporary image and draw object to measure text
    temp_img = Image.new('RGBA', (1, 1), (255, 255, 255, 0))
    draw = ImageDraw.Draw(temp_img)
    font = _load_font(font_size, font_name)
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    
    return width, height


def is_font_available(font_name: str) -> bool:
    """Check if a specific font is available on the system.
    
    Args:
        font_name: Name of the font to check
    
    Returns:
        True if font is available, False otherwise
    """
    try:
        # Try to load the font with a small size
        ImageFont.truetype(font_name, 10)
        return True
    except Exception:
        return False


