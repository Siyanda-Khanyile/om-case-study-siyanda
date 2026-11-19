"""Validate Terraform's JSON configuration syntax (a `.tf.json` file)."""

from tfvalidator.domain import terraform_spec as spec
from tfvalidator.domain.findings import Findings


class ConfigValidator(object):
    """Checks that each recognised top-level block has a usable body.

    A block body is an object, or an array when the block legitimately repeats
    (several `provider` blocks, for instance).
    """

    def validate(self, document):
        findings = Findings()
        expected = " or ".join(kind.__name__ for kind in spec.BLOCK_BODY_TYPES)

        for block in sorted(set(document) & spec.HCL_JSON_BLOCKS):
            body = document[block]
            if not isinstance(body, spec.BLOCK_BODY_TYPES):
                findings.add_problem(
                    "%r block is a %s, expected %s" % (block, type(body).__name__, expected)
                )
        return findings
