from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple

from PIL import Image

from .naming import build_output_name
from .types import ExportOptions, NamingMode, ResizeMode


def _ensure_output_dir(options: ExportOptions, source_dirs: List[Path]) -> None:
    out = options.output_dir
    out.mkdir(parents=True, exist_ok=True)

    if options.allow_overwrite_source:
        return

    # Forbid exporting directly into any source directory by default
    for src in source_dirs:
        try:
            if out.resolve() == src.resolve():
                raise ValueError(
                    f"Output directory {out} must differ from source directory {src}."
                )
        except FileNotFoundError:
            # In case of non-existing dirs, skip
            continue


def _compute_new_size(img: Image.Image, options: ExportOptions) -> Tuple[int, int]:
    w, h = img.width, img.height
    mode = options.resize_mode
    val = options.resize_value

    if mode == ResizeMode.NONE or val is None:
        return (w, h)

    if mode == ResizeMode.BY_WIDTH:
        new_w = int(val)
        if options.keep_aspect_ratio:
            new_h = max(1, int(h * (new_w / w)))
        else:
            new_h = h
        return (max(1, new_w), max(1, new_h))

    if mode == ResizeMode.BY_HEIGHT:
        new_h = int(val)
        if options.keep_aspect_ratio:
            new_w = max(1, int(w * (new_h / h)))
        else:
            new_w = w
        return (max(1, new_w), max(1, new_h))

    if mode == ResizeMode.BY_PERCENT:
        scale = max(0.01, float(val) / 100.0)
        return (max(1, int(w * scale)), max(1, int(h * scale)))

    return (w, h)


def export_images(
    src_files: Iterable[Path],
    options: ExportOptions,
) -> List[Path]:
    """Export given images to the output directory using options.

    - Respects JPEG/PNG output
    - Applies name rules (keep/prefix/suffix)
    - Applies optional resizing
    - Applies JPEG quality
    - Returns list of exported file paths
    """
    files = list(src_files)
    if not files:
        return []

    source_dirs = sorted({p.parent for p in files})
    _ensure_output_dir(options, source_dirs)

    exported: List[Path] = []
    for src in files:
        # Build destination path
        dest = build_output_name(
            src_file=src,
            out_dir=options.output_dir,
            mode=options.naming_mode,
            prefix=options.prefix,
            suffix=options.suffix,
            out_ext=options.output_format,
        )

        # Open and optionally resize
        with Image.open(src) as img:
            # Convert mode for JPEG if needed
            save_kwargs = {}
            if options.output_format.lower() == "jpeg":
                save_kwargs["quality"] = max(0, min(100, int(options.jpeg_quality)))
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")

            new_size = _compute_new_size(img, options)
            if new_size != (img.width, img.height):
                img = img.resize(new_size, resample=Image.Resampling.LANCZOS)

            # Save
            dest.parent.mkdir(parents=True, exist_ok=True)
            if options.output_format.lower() == "jpeg":
                img.save(dest, format="JPEG", **save_kwargs)
            else:
                img.save(dest, format="PNG")

        exported.append(dest)

    return exported


