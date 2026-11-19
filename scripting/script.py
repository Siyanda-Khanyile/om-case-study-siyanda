#!/usr/bin/env python3
"""Validate the Terraform JSON files sitting next to this script.

Usage:
    python3 script.py                       # every JSON file in this directory
    python3 script.py plan.json other.json  # specific files

Exits 0 when every file is valid Terraform IaC, 1 when any file is flagged.

The implementation lives in the `tfvalidator` package beside this file:

    tfvalidator/domain          Terraform rules and value objects (no I/O)
    tfvalidator/infrastructure  finding and loading files
    tfvalidator/application     the use case wiring the two together
    tfvalidator/interface       the CLI and its output format

This module only puts its own directory on the import path (so it runs from any
working directory, and under `python3 -I`) and delegates to the CLI.
"""

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from tfvalidator.application.file_validation_service import (  # noqa: E402
    FileValidationService,
    validate_json_files,
    validate_terraform_json,
)
from tfvalidator.domain.document_kind import DocumentKind  # noqa: E402
from tfvalidator.domain.validation_result import ValidationResult  # noqa: E402
from tfvalidator.infrastructure.json_file_finder import list_json_files  # noqa: E402
from tfvalidator.interface.cli import main  # noqa: E402

__all__ = [
    "DocumentKind",
    "FileValidationService",
    "ValidationResult",
    "list_json_files",
    "main",
    "validate_json_files",
    "validate_terraform_json",
]


if __name__ == "__main__":
    sys.exit(main())
