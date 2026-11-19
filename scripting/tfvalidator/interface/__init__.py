"""Presentation: turn results into something a human or a CI job can read."""

from tfvalidator.interface.cli import ValidationCli, build_parser, main
from tfvalidator.interface.palette import Palette
from tfvalidator.interface.report_formatter import ConsoleReportFormatter
from tfvalidator.interface.table_report_formatter import TableReportFormatter

__all__ = [
    "ConsoleReportFormatter", "Palette", "TableReportFormatter",
    "ValidationCli", "build_parser", "main",
]
