from __future__ import annotations

from typing import Tuple

from .types import GridPosition


def compute_position(
    img_w: int,
    img_h: int,
    box_w: int,
    box_h: int,
    position: GridPosition,
    margin: int = 20,
) -> Tuple[int, int]:
    """Compute top-left coordinate for placing a box within an image.

    Ensures the placement respects provided margins and clamps within bounds.
    """
    # Initial placement based on grid
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

    # Clamp to ensure visibility
    x = max(0, min(x, img_w - box_w))
    y = max(0, min(y, img_h - box_h))
    return x, y


