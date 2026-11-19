"""Command-line entry point."""

import argparse
import sys
from pathlib import Path

from tfvalidator.application.file_validation_service import FileValidationService
from tfvalidator.infrastructure.json_file_finder import DEFAULT_DIRECTORY
from tfvalidator.interface.palette import Palette
from tfvalidator.interface.report_formatter import ConsoleReportFormatter
from tfvalidator.interface.table_report_formatter import TableReportFormatter


def _home_relative(path):
    """Render `path` with the home directory abbreviated to `~`."""
    try:
        return "~/%s" % Path(path).relative_to(Path.home())
    except ValueError:
        return str(path)


def build_parser():
    parser = argparse.ArgumentParser(
        prog="script.py",
        description="Validate JSON files as Terraform IaC (plans, state, config, schemas).",
        epilog="Exits 0 when every file is valid, 1 when any file is flagged.",
    )
    parser.add_argument(
        "paths", nargs="*", type=Path,
        help="files to validate (default: every JSON file beside script.py)",
    )
    parser.add_argument(
        "--plain", action="store_true",
        help="one line per file instead of a table (easier to grep)",
    )
    parser.add_argument(
        "--ascii", action="store_true",
        help="draw the table with ASCII instead of box-drawing characters",
    )
    parser.add_argument(
        "--color", dest="color", action="store_const", const=True, default=None,
        help="force colour output",
    )
    parser.add_argument(
        "--no-color", dest="color", action="store_const", const=False,
        help="disable colour output",
    )
    parser.add_argument(
        "--width", type=int, default=None,
        help="assume this terminal width when sizing the table",
    )
    return parser


class ValidationCli(object):
    """Prints a validation report and reports success through the exit code.

    Exits 0 when every file validated, 1 when any file was flagged, so the
    command can gate a pipeline. The table is the default view; `--plain`
    switches to one line per file.
    """

    def __init__(self, service=None, formatter=None, stream=None):
        self._service = service or FileValidationService()
        self._formatter = formatter
        self._stream = stream or sys.stdout

    def run(self, argv=None):
        args = build_parser().parse_args(sys.argv[1:] if argv is None else list(argv))

        if args.paths:
            results = self._service.validate_files(args.paths)
            scope = "%d file(s)" % len(args.paths)
        else:
            results = self._service.validate_directory()
            scope = _home_relative(DEFAULT_DIRECTORY)
            if not results:
                self._write("No JSON files found in %s" % DEFAULT_DIRECTORY)
                return 0

        for line in self._select_formatter(args, scope).format_report(results):
            self._write(line)
        return 1 if any(not result.is_valid for result in results) else 0

    def _select_formatter(self, args, scope):
        if self._formatter is not None:
            return self._formatter
        if args.plain:
            return ConsoleReportFormatter()
        return TableReportFormatter(
            palette=Palette.for_stream(self._stream, args.color),
            width=args.width,
            ascii_only=args.ascii,
            title="Terraform JSON validation  %s" % scope,
        )

    def _write(self, line):
        self._stream.write(line + "\n")


def main(argv=None):
    return ValidationCli().run(argv)
