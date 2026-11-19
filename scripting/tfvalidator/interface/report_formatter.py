"""Rendering of validation results as plain text."""


class ConsoleReportFormatter(object):
    """Formats `ValidationResult` objects as lines of console output."""

    def format_report(self, results):
        lines = []
        for result in results:
            lines.extend(self.format_result(result))
        lines.append("")
        lines.append(self.format_summary(results))
        return lines

    def format_result(self, result):
        if result.is_valid:
            lines = ["OK      %s  (%s)" % (result.name, result.kind_label)]
        else:
            lines = ["FLAGGED %s  (not valid Terraform IaC)" % result.name]
        lines.extend("          problem: %s" % problem for problem in result.problems)
        lines.extend("          note:    %s" % note for note in result.notes)
        return lines

    def format_summary(self, results):
        flagged = sum(1 for result in results if not result.is_valid)
        return "%d of %d file(s) valid, %d flagged." % (
            len(results) - flagged, len(results), flagged,
        )
