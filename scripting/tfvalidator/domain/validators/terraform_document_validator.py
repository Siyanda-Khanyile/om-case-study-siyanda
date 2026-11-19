"""Classify a parsed document, then apply the checks for its kind."""

from tfvalidator.domain.document_kind import DocumentKind
from tfvalidator.domain.findings import Findings
from tfvalidator.domain.validation_result import ValidationResult
from tfvalidator.domain.validators.config_validator import ConfigValidator
from tfvalidator.domain.validators.document_classifier import DocumentClassifier
from tfvalidator.domain.validators.plan_validator import PlanValidator
from tfvalidator.domain.validators.provider_schema_validator import ProviderSchemaValidator
from tfvalidator.domain.validators.state_validator import StateValidator


class TerraformDocumentValidator(object):
    """Validates an already-parsed JSON document as Terraform IaC.

    This is the pure entry point to the domain: give it a Python object and it
    returns a `ValidationResult` without reading anything from disk. The
    per-kind validators can be replaced for testing.
    """

    def __init__(self, classifier=None, validators=None):
        self._classifier = classifier or DocumentClassifier()
        self._validators = validators or {
            DocumentKind.PLAN: PlanValidator(),
            DocumentKind.STATE: StateValidator(),
            DocumentKind.CONFIG: ConfigValidator(),
            DocumentKind.PROVIDER_SCHEMA: ProviderSchemaValidator(),
        }

    def validate(self, document, path="<document>"):
        classification = self._classifier.classify(document)
        findings = Findings().extend(classification.findings)

        validator = self._validators.get(classification.kind)
        if validator is not None:
            findings.extend(validator.validate(document))

        return ValidationResult.from_findings(path, classification.kind, findings)
