from __future__ import annotations

from pathlib import Path

from .types import NamingMode


def build_output_name(
    src_file: Path,
    out_dir: Path,
    mode: NamingMode,
    prefix: str = "",
    suffix: str = "",
    out_ext: str = "jpeg",
) -> Path:
    """Construct output file path based on naming rules.

    - mode KEEP: keep original basename
    - mode PREFIX: prepend prefix
    - mode SUFFIX: append suffix before extension
    - out_ext is logical format ("jpeg" or "png")
    """
    stem = src_file.stem
    if mode == NamingMode.PREFIX:
        stem = f"{prefix}{stem}"
    elif mode == NamingMode.SUFFIX:
        stem = f"{stem}{suffix}"

    # Normalize extension
    ext = ".jpg" if out_ext.lower() == "jpeg" else ".png"
    return out_dir / f"{stem}{ext}"


