"""Example: Apply a text watermark to all discovered images.

Run:
    python -m examples.text_watermark_example "./photos" --out ./out --text "Demo" --font-size 48 --color "255,0,0" --opacity 80 --pos bottom_right
"""

from __future__ import annotations

import argparse
from pathlib import Path

from file_processing import (
    ExportOptions,
    NamingMode,
    ResizeMode,
    discover_inputs,
    export_images,
)
from watermarking import GridPosition, TextWatermarkOptions, apply_text_watermark
from PIL import Image


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Text watermark example")
    p.add_argument("inputs", nargs="+", help="Input files or folders")
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--text", required=True, help="Watermark text")
    p.add_argument("--font-size", type=int, default=24)
    p.add_argument("--color", default="255,255,255", help="R,G,B")
    p.add_argument("--opacity", type=int, default=100)
    p.add_argument(
        "--pos",
        choices=[
            "top_left","top_center","top_right",
            "center_left","center","center_right",
            "bottom_left","bottom_center","bottom_right",
        ],
        default="bottom_right",
    )
    return p.parse_args()


def _parse_color(rgb: str) -> tuple[int, int, int]:
    parts = [int(x) for x in rgb.split(",")]
    if len(parts) != 3:
        raise ValueError("Color must be R,G,B")
    return tuple(max(0, min(255, v)) for v in parts)  # type: ignore[return-value]


def main() -> None:
    args = parse_args()

    imp = discover_inputs(args.inputs)
    print(f"Discovered {len(imp.files)} files under {imp.common_root}")

    # Prepare watermark options
    wm_options = TextWatermarkOptions(
        text=args.text,
        font_size=args.font_size,
        color=_parse_color(args.color),
        opacity=args.opacity,
        position=GridPosition(args.pos),
    )

    # Render and export
    out_dir = Path(args.out)
    exported_paths = []
    for src in imp.files:
        with Image.open(src) as img:
            watermarked = apply_text_watermark(img, wm_options)
            # Reuse exporter for consistent naming/output
            opts = ExportOptions(
                output_dir=out_dir,
                output_format="jpeg" if img.format == "JPEG" else "png",
                naming_mode=NamingMode.SUFFIX,
                suffix="_watermarked",
            )
            # Save directly to destination path following naming rules
            # (Export via exporter would reopen the file; we save directly here.)
            dest = out_dir / f"{src.stem}_watermarked.{ 'jpg' if opts.output_format=='jpeg' else 'png'}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            if opts.output_format == "jpeg":
                watermarked.convert("RGB").save(dest, format="JPEG", quality=90)
            else:
                watermarked.save(dest, format="PNG")
            exported_paths.append(dest)

    print(f"Exported {len(exported_paths)} files to {out_dir}")


if __name__ == "__main__":
    main()


