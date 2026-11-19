"""The outcome of trying to turn a file into a JSON document."""


class LoadOutcome(object):
    """Either a parsed `document` or an `error` explaining why there is none."""

    def __init__(self, document=None, error=None):
        self.document = document
        self.error = error

    @classmethod
    def loaded(cls, document):
        return cls(document=document)

    @classmethod
    def failed_with(cls, error):
        return cls(error=error)

    @property
    def failed(self):
        return self.error is not None
