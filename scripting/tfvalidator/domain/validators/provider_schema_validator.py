"""Validate a provider schema document."""

from tfvalidator.domain.findings import Findings


class ProviderSchemaValidator(object):
    """Checks a `terraform providers schema -json` document.

    A schema is valid Terraform output but declares no infrastructure, which is
    worth noting when the caller expected a plan.
    """

    def validate(self, document):
        findings = Findings()

        schemas = document.get("provider_schemas")
        if not isinstance(schemas, dict):
            findings.add_problem(
                "provider_schemas is a %s, expected an object" % type(schemas).__name__
            )
            return findings

        findings.add_note(
            "provider schema for %d provider(s); it declares no infrastructure" % len(schemas)
        )
        return findings
