from __future__ import annotations

from typing import Tuple, Optional

from .types import GridPosition


def compute_position(
    img_w: int,
    img_h: int,
    box_w: int,
    box_h: int,
    position: GridPosition,
    margin: int = 20,
) -> Tuple[int, int]:
    """Compute top-left coordinate for placing a box within an image based on nine-grid layout.

    Args:
        img_w: Width of the image in pixels
        img_h: Height of the image in pixels
        box_w: Width of the watermark box in pixels
        box_h: Height of the watermark box in pixels
        position: GridPosition enum value representing the preset position
        margin: Margin from the image edges in pixels

    Returns:
        Tuple of (x, y) coordinates for the top-left corner of the watermark
    """
    # Initial placement based on nine-grid layout
    if position == GridPosition.TOP_LEFT:
        x = margin
        y = margin
    elif position == GridPosition.TOP_CENTER:
        x = (img_w - box_w) // 2
        y = margin
    elif position == GridPosition.TOP_RIGHT:
        x = img_w - box_w - margin
        y = margin
    elif position == GridPosition.CENTER_LEFT:
        x = margin
        y = (img_h - box_h) // 2
    elif position == GridPosition.CENTER:
        x = (img_w - box_w) // 2
        y = (img_h - box_h) // 2
    elif position == GridPosition.CENTER_RIGHT:
        x = img_w - box_w - margin
        y = (img_h - box_h) // 2
    elif position == GridPosition.BOTTOM_LEFT:
        x = margin
        y = img_h - box_h - margin
    elif position == GridPosition.BOTTOM_CENTER:
        x = (img_w - box_w) // 2
        y = img_h - box_h - margin
    else:  # GridPosition.BOTTOM_RIGHT
        x = img_w - box_w - margin
        y = img_h - box_h - margin

    # Clamp to ensure visibility - prevent watermark from going out of bounds
    x = max(0, min(x, img_w - box_w))
    y = max(0, min(y, img_h - box_h))
    return x, y


def validate_position_within_bounds(
    img_w: int,
    img_h: int,
    box_w: int,
    box_h: int,
    x: int,
    y: int,
) -> Tuple[int, int]:
    """Ensure the watermark position stays within the image bounds.
    
    Args:
        img_w: Width of the image in pixels
        img_h: Height of the image in pixels
        box_w: Width of the watermark box in pixels
        box_h: Height of the watermark box in pixels
        x: Current x-coordinate of the watermark
        y: Current y-coordinate of the watermark
    
    Returns:
        Tuple of (x, y) coordinates clamped to the image bounds
    """
    # Clamp position to ensure watermark remains fully visible
    clamped_x = max(0, min(x, img_w - box_w))
    clamped_y = max(0, min(y, img_h - box_h))
    return clamped_x, clamped_y


def get_position_name(position: GridPosition) -> str:
    """Get human-readable name for a GridPosition.
    
    Args:
        position: GridPosition enum value
    
    Returns:
        Human-readable string representation of the position
    """
    position_names = {
        GridPosition.TOP_LEFT: "左上",
        GridPosition.TOP_CENTER: "中上",
        GridPosition.TOP_RIGHT: "右上",
        GridPosition.CENTER_LEFT: "左中",
        GridPosition.CENTER: "正中",
        GridPosition.CENTER_RIGHT: "右中",
        GridPosition.BOTTOM_LEFT: "左下",
        GridPosition.BOTTOM_CENTER: "中下",
        GridPosition.BOTTOM_RIGHT: "右下",
    }
    return position_names.get(position, "右下")


