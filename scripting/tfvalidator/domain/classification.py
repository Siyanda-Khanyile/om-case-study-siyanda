"""The result of deciding what kind of document something is."""

from tfvalidator.domain.findings import Findings


class Classification(object):
    """A detected `DocumentKind` (or None) plus the findings from detecting it."""

    def __init__(self, kind=None, findings=None):
        self.kind = kind
        self.findings = findings if findings is not None else Findings()

    @property
    def is_terraform(self):
        return self.kind is not None

    def __repr__(self):
        return "Classification(kind=%r, findings=%r)" % (self.kind, self.findings)
