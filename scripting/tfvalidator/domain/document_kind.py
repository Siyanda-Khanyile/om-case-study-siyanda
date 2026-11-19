"""The kinds of Terraform document that can legitimately appear as JSON."""

from enum import Enum


class DocumentKind(Enum):
    """A recognised Terraform JSON document kind.

    The value doubles as the human-readable label used in reports.
    """

    PLAN = "terraform plan"
    STATE = "terraform state"
    CONFIG = "terraform config (.tf.json)"
    PROVIDER_SCHEMA = "terraform provider schema"

    def __str__(self):
        return self.value
