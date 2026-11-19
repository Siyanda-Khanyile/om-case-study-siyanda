"""The verdict for a single document."""

from pathlib import Path


class ValidationResult(object):
    """Outcome of validating one JSON file as Terraform IaC.

    `kind` is the detected `DocumentKind` (None if it is not Terraform at all),
    `problems` are the reasons it is not usable as Terraform IaC, and `notes`
    are non-fatal observations. The result is valid when a kind was detected
    and there are no problems. The `path` is carried for reporting only; this
    object never touches the filesystem.
    """

    def __init__(self, path, kind=None, problems=None, notes=None):
        self.path = Path(path)
        self.kind = kind
        self.problems = list(problems or [])
        self.notes = list(notes or [])

    @classmethod
    def from_findings(cls, path, kind, findings):
        return cls(path, kind, findings.problems, findings.notes)

    @property
    def is_valid(self):
        return self.kind is not None and not self.problems

    @property
    def name(self):
        return self.path.name

    @property
    def kind_label(self):
        return str(self.kind) if self.kind is not None else "unknown"

    def __repr__(self):
        return "ValidationResult(path=%r, kind=%r, valid=%r, problems=%r)" % (
            self.name, self.kind_label, self.is_valid, self.problems,
        )
