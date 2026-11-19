"""Decide which kind of Terraform document a parsed JSON value is."""

from tfvalidator.domain import terraform_spec as spec
from tfvalidator.domain.classification import Classification
from tfvalidator.domain.document_kind import DocumentKind
from tfvalidator.domain.findings import Findings


class DocumentClassifier(object):
    """Classifies a parsed JSON document as a Terraform document kind.

    Machine-readable output (`terraform show -json`) is identified by its
    `format_version`; configuration files are identified by their top-level
    block types. Anything else is reported as not being Terraform at all.
    """

    def classify(self, document):
        findings = Findings()

        if not isinstance(document, dict):
            findings.add_problem(
                "top level is a JSON %s, but every Terraform document is an object"
                % type(document).__name__
            )
            return Classification(None, findings)

        if "format_version" in document:
            return self._classify_machine_readable(document, findings)
        return self._classify_config(document, findings)

    def _classify_machine_readable(self, document, findings):
        self._check_format_version(document.get("format_version"), findings)

        if "provider_schemas" in document:
            return Classification(DocumentKind.PROVIDER_SCHEMA, findings)
        if spec.PLAN_MARKER_KEYS & set(document):
            return Classification(DocumentKind.PLAN, findings)
        if "values" in document:
            return Classification(DocumentKind.STATE, findings)

        findings.add_problem(
            "has format_version but none of planned_values, resource_changes, "
            "configuration or values, so it is neither a plan nor a state"
        )
        return Classification(None, findings)

    def _check_format_version(self, format_version, findings):
        if not isinstance(format_version, str):
            findings.add_problem("format_version is not a string")
            return
        try:
            major = int(format_version.split(".")[0])
        except ValueError:
            findings.add_problem("format_version %r is not a version number" % format_version)
            return
        if major != spec.SUPPORTED_FORMAT_MAJOR:
            findings.add_note(
                "format_version %s is outside the supported %d.x range; fields may differ"
                % (format_version, spec.SUPPORTED_FORMAT_MAJOR)
            )

    def _classify_config(self, document, findings):
        keys = set(document)
        if not keys:
            findings.add_problem("empty JSON object: no Terraform content")
            return Classification(None, findings)

        recognised = keys & spec.HCL_JSON_BLOCKS
        if not recognised:
            findings.add_problem(
                "no Terraform structure found; top-level keys are %s"
                % ", ".join(sorted(keys)[:6])
            )
            return Classification(None, findings)

        unknown = sorted(keys - spec.HCL_JSON_BLOCKS)
        if unknown:
            findings.add_note("ignoring non-Terraform top-level keys: %s" % ", ".join(unknown))
        return Classification(DocumentKind.CONFIG, findings)
