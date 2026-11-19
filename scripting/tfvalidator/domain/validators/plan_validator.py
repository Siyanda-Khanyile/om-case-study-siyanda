"""Validate a Terraform plan representation."""

from tfvalidator.domain.findings import Findings
from tfvalidator.domain.validators.resource_change_validator import ResourceChangeValidator


class PlanValidator(object):
    """Checks a plan document beyond its classification.

    An empty plan is structurally valid, so "nothing to apply" is reported as a
    note rather than a problem; whether an apply should proceed is a separate
    policy question.
    """

    def __init__(self, resource_change_validator=None):
        self._resource_changes = resource_change_validator or ResourceChangeValidator()

    def validate(self, document):
        findings = Findings()

        if not isinstance(document.get("terraform_version"), str):
            findings.add_problem("plan is missing a string terraform_version")

        findings.extend(self._resource_changes.validate(document))

        if not document.get("resource_changes"):
            findings.add_note("plan contains no resource changes (nothing to apply)")
        if document.get("errored"):
            findings.add_note("plan is marked errored; Terraform did not finish planning")
        elif document.get("applyable") is False:
            findings.add_note("plan is marked not applyable")

        return findings
