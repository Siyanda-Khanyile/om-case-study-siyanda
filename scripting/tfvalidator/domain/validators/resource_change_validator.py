"""Validate the `resource_changes` list of a plan representation."""

from tfvalidator.domain import terraform_spec as spec
from tfvalidator.domain.findings import Findings


class ResourceChangeValidator(object):
    """Checks that each planned resource change has the shape Terraform emits.

    Every entry needs an address, type and name, and a `change` object with at
    least one action drawn from Terraform's known action set. Downstream
    policy checks rely on these fields being present.
    """

    def validate(self, document):
        findings = Findings()
        if "resource_changes" not in document:
            return findings

        changes = document["resource_changes"]
        if not isinstance(changes, list):
            return findings.add_problem(
                "resource_changes is a %s, expected a list" % type(changes).__name__
            )

        for index, change in enumerate(changes):
            self._validate_entry(index, change, findings)
        return findings

    def _validate_entry(self, index, change, findings):
        label = "resource_changes[%d]" % index

        if not isinstance(change, dict):
            findings.add_problem(
                "%s is a %s, expected an object" % (label, type(change).__name__)
            )
            return

        missing = [field for field in spec.RESOURCE_CHANGE_FIELDS if field not in change]
        if missing:
            findings.add_problem("%s is missing %s" % (label, ", ".join(missing)))

        detail = change.get("change")
        if not isinstance(detail, dict):
            findings.add_problem("%s has no change object" % label)
            return

        actions = detail.get("actions")
        if not isinstance(actions, list) or not actions:
            findings.add_problem("%s.change.actions is missing or empty" % label)
            return

        unknown = [action for action in actions if action not in spec.PLAN_ACTIONS]
        if unknown:
            findings.add_problem(
                "%s.change.actions contains unrecognised %s"
                % (label, ", ".join(repr(action) for action in unknown))
            )
