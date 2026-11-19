"""Validate a Terraform state representation."""

from tfvalidator.domain.findings import Findings


class StateValidator(object):
    """Checks that a state document carries a usable `values` tree."""

    def validate(self, document):
        findings = Findings()

        if not isinstance(document.get("terraform_version"), str):
            findings.add_problem("state is missing a string terraform_version")

        values = document.get("values")
        if not isinstance(values, dict):
            findings.add_problem(
                "values is a %s, expected an object" % type(values).__name__
            )
            return findings

        if "root_module" not in values:
            findings.add_note("state has no root_module; it describes no resources")
        return findings
