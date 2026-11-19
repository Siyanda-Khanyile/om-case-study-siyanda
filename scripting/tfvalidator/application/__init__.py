"""Use cases: wire the domain rules to the filesystem."""

from tfvalidator.application.file_validation_service import (
    FileValidationService,
    validate_json_files,
    validate_terraform_json,
)

__all__ = ["FileValidationService", "validate_json_files", "validate_terraform_json"]
