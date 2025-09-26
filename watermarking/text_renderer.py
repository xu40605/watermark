from __future__ import annotations

from typing import Tuple

from PIL import Image, ImageDraw, ImageFont

from .positioning import compute_position
from .types import GridPosition, TextWatermarkOptions


def _load_font(font_size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Attempt to load a system font; fallback to default.

    On Windows, tries Arial; otherwise falls back to PIL's default bitmap font.
    """
    try:
        return ImageFont.truetype("arial.ttf", font_size)
    except Exception:
        try:
            return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
        except Exception:
            return ImageFont.load_default()


def _clamp_opacity(opacity: int) -> int:
    return max(0, min(100, int(opacity)))


def apply_text_watermark(
    image: Image.Image,
    options: TextWatermarkOptions,
) -> Image.Image:
    """Render a text watermark onto a copy of the provided image.

    - Respects opacity (0-100), color, font size
    - Places watermark using nine-grid presets with margins
    - Ensures result remains within bounds
    """
    if options.opacity <= 0 or not options.text:
        return image.copy()

    # Work in RGBA to support alpha compositing
    base = image.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font = _load_font(options.font_size)
    bbox = draw.textbbox((0, 0), options.text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

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


