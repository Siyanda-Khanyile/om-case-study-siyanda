"""Problems and notes accumulated while validating a document."""


class Findings(object):
    """A mutable collection of validation findings.

    `problems` make a document invalid as Terraform IaC. `notes` are
    observations worth surfacing that do not, on their own, invalidate it.
    """

    def __init__(self, problems=None, notes=None):
        self.problems = list(problems or [])
        self.notes = list(notes or [])

    def add_problem(self, message):
        self.problems.append(message)
        return self

    def add_note(self, message):
        self.notes.append(message)
        return self

    def extend(self, other):
        """Absorb another `Findings` instance."""
        self.problems.extend(other.problems)
        self.notes.extend(other.notes)
        return self

    @property
    def has_problems(self):
        return bool(self.problems)

    def __repr__(self):
        return "Findings(problems=%r, notes=%r)" % (self.problems, self.notes)
