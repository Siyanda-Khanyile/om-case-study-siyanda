"""The use case: validate Terraform JSON files on disk."""

from pathlib import Path

from tfvalidator.domain.validation_result import ValidationResult
from tfvalidator.domain.validators.terraform_document_validator import TerraformDocumentValidator
from tfvalidator.infrastructure.json_file_finder import JsonFileFinder
from tfvalidator.infrastructure.json_file_loader import JsonFileLoader


class FileValidationService(object):
    """Finds, loads and validates Terraform JSON files.

    Collaborators are injected, so tests can supply an in-memory loader or a
    stub finder and exercise the rules without touching a filesystem.
    """

    def __init__(self, finder=None, loader=None, validator=None):
        self._finder = finder or JsonFileFinder()
        self._loader = loader or JsonFileLoader()
        self._validator = validator or TerraformDocumentValidator()

    def validate_file(self, path):
        """Validate one file. Returns a `ValidationResult`."""
        path = Path(path)
        outcome = self._loader.load(path)
        if outcome.failed:
            return ValidationResult(path, problems=[outcome.error])
        return self._validator.validate(outcome.document, path)

    def validate_files(self, paths):
        """Validate each given path, preserving order."""
        return [self.validate_file(path) for path in paths]

    def validate_directory(self, directory=None):
        """Validate every JSON file directly inside `directory`."""
        return self.validate_files(self._finder.find(directory))


def validate_terraform_json(path):
    """Validate a single file using the default collaborators."""
    return FileValidationService().validate_file(path)


def validate_json_files(directory=None):
    """Validate every JSON file in `directory` (defaults to script.py's folder)."""
    return FileValidationService().validate_directory(directory)
