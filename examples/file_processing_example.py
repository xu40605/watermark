"""Example usage of the file_processing package.

Run:
    python -m examples.file_processing_example "./photos" --out ./out --format png --mode suffix --suffix _watermarked --resize by_width --value 1600
"""

from __future__ import annotations

import argparse
from pathlib import Path

from file_processing import (
    NamingMode,
    ResizeMode,
    ExportOptions,
    discover_inputs,
    export_images,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="File processing example")
    p.add_argument("inputs", nargs="+", help="Input files or folders")
    p.add_argument("--out", required=True, help="Output directory")
    p.add_argument("--format", choices=["jpeg", "png"], default="jpeg")
    p.add_argument("--mode", choices=[m.value for m in NamingMode], default="keep")
    p.add_argument("--prefix", default="")
    p.add_argument("--suffix", default="")
    p.add_argument("--quality", type=int, default=90)
    p.add_argument("--resize", choices=[m.value for m in ResizeMode], default="none")
    p.add_argument("--value", type=int, help="Resize width/height/percent depending on mode")
    p.add_argument("--no-keep-aspect", dest="no_keep_aspect", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    imp = discover_inputs(args.inputs)
    print(f"Discovered {len(imp.files)} files under {imp.common_root}")

    options = ExportOptions(
        output_dir=Path(args.out),
        output_format=args.format,
        naming_mode=NamingMode(args.mode),
        prefix=args.prefix,
        suffix=args.suffix,
        jpeg_quality=args.quality,
        resize_mode=ResizeMode(args.resize),
        resize_value=args.value,
        keep_aspect_ratio=not args.no_keep_aspect,
        allow_overwrite_source=False,
    )

    exported = export_images(imp.files, options)
    print(f"Exported {len(exported)} files to {options.output_dir}")


if __name__ == "__main__":
    main()


