"""Reading and parsing JSON files, with failures turned into domain outcomes."""

import json
from pathlib import Path

from tfvalidator.domain.load_outcome import LoadOutcome


class JsonFileLoader(object):
    """Loads a JSON file, reporting failures instead of raising.

    Unreadable, non-UTF-8 and malformed files are all answered with a failed
    `LoadOutcome` carrying a human-readable reason, so one bad file never stops
    a batch run.
    """

    def load(self, path):
        path = Path(path)
        try:
            with path.open(encoding="utf-8") as handle:
                return LoadOutcome.loaded(json.load(handle))
        except OSError as error:
            reason = error.strerror or str(error)
            return LoadOutcome.failed_with("cannot read file: %s" % reason)
        except UnicodeDecodeError:
            return LoadOutcome.failed_with("not UTF-8 encoded text")
        except json.JSONDecodeError as error:
            return LoadOutcome.failed_with(
                "not valid JSON: %s (line %d, column %d)"
                % (error.msg, error.lineno, error.colno)
            )
