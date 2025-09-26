"""File processing package for the Watermark Desktop App.

This package provides functionality for:
- Discovering and validating image inputs (single, multiple, folders)
- Enforcing supported formats
- Generating export file names with configurable rules
- Exporting images with optional JPEG quality and resizing
- Safety checks to prevent overwriting sources

Modules:
- types: Shared enums and dataclasses
- formats: Supported format logic
- importer: Input discovery utilities
- naming: Output file naming rules
- exporter: Export orchestration and image IO helpers
"""

from .types import NamingMode, ResizeMode, ExportOptions, ImportResult
from .formats import SUPPORTED_INPUT_EXTS, SUPPORTED_OUTPUT_EXTS, is_supported_input
from .importer import discover_inputs
from .naming import build_output_name
from .exporter import export_images

__all__ = [
    "NamingMode",
    "ResizeMode",
    "ExportOptions",
    "ImportResult",
    "SUPPORTED_INPUT_EXTS",
    "SUPPORTED_OUTPUT_EXTS",
    "is_supported_input",
    "discover_inputs",
    "build_output_name",
    "export_images",
]


