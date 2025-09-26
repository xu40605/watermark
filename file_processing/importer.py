from __future__ import annotations

from pathlib import Path
from typing import Iterable, List

from .formats import is_supported_input
from .types import ImportResult


def _iter_folder_images(folder: Path) -> List[Path]:
    files: List[Path] = []
    for p in folder.rglob("*"):
        if p.is_file() and is_supported_input(p):
            files.append(p)
    return files


def discover_inputs(paths: Iterable[str | Path]) -> ImportResult:
    """Discover image inputs given file and/or folder paths.

    - Accepts single/multiple files, or folders (recursively).
    - Returns a list of unique files sorted by path, and the common root dir.
    """
    unique: List[Path] = []
    seen = set()
    roots: List[Path] = []

    for raw in paths:
        p = Path(raw).expanduser().resolve()
        if p.is_dir():
            roots.append(p)
            for f in _iter_folder_images(p):
                if f not in seen:
                    unique.append(f)
                    seen.add(f)
        elif p.is_file():
            roots.append(p.parent)
            if is_supported_input(p) and p not in seen:
                unique.append(p)
                seen.add(p)

    unique.sort()

    # Determine common root
    if not roots:
        common_root = Path.cwd()
    else:
        common_root = Path(
            str(Path(*Path.commonpath([str(r) for r in roots]).split("/")))
        )

    return ImportResult(files=unique, common_root=common_root)


