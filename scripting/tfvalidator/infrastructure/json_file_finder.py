"""Discovery of JSON files on disk."""

from pathlib import Path

# The directory holding script.py, i.e. the package's parent.
DEFAULT_DIRECTORY = Path(__file__).resolve().parents[2]


class JsonFileFinder(object):
    """Finds the JSON files sitting directly in a directory."""

    def __init__(self, default_directory=DEFAULT_DIRECTORY):
        self._default_directory = Path(default_directory)

    def find(self, directory=None):
        """Return the JSON files located directly in `directory`.

        Defaults to the directory containing `script.py`, so the result is the
        same no matter which working directory the caller runs from. Only files
        are returned (a directory named `foo.json` is ignored), nested
        directories are not searched, and the `.json` suffix is matched
        case-insensitively. Files come back sorted by name as absolute paths.
        """
        directory = Path(directory or self._default_directory).resolve()
        return sorted(
            (
                entry
                for entry in directory.iterdir()
                if entry.is_file() and entry.suffix.lower() == ".json"
            ),
            key=lambda entry: entry.name,
        )


def list_json_files(directory=DEFAULT_DIRECTORY):
    """Convenience wrapper around `JsonFileFinder.find`."""
    return JsonFileFinder().find(directory)
