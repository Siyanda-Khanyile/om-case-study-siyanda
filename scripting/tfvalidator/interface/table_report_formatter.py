"""Rendering of validation results as a bordered table."""

import shutil
import textwrap

from tfvalidator.interface.palette import Palette

# Box-drawing glyph sets. ASCII keeps the layout intact where the terminal or
# font cannot render the Unicode set.
UNICODE_BOX = {
    "h": "─", "v": "│",
    "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯",
    "head_l": "├", "head_r": "┤", "head_x": "┼",
    "row_l": "├", "row_r": "┤", "row_x": "┼",
    "top_x": "┬", "bot_x": "┴",
    "ok": "✔", "bad": "✘", "problem": "✘",
    "note": "•", "none": "—", "ellipsis": "…",
}
ASCII_BOX = {
    "h": "-", "v": "|",
    "tl": "+", "tr": "+", "bl": "+", "br": "+",
    "head_l": "+", "head_r": "+", "head_x": "+",
    "row_l": "+", "row_r": "+", "row_x": "+",
    "top_x": "+", "bot_x": "+",
    "ok": "", "bad": "", "problem": "!",
    "note": "-", "none": "-", "ellipsis": "...",
}

HEADERS = ("STATUS", "FILE", "KIND", "DETAILS")
MIN_DETAILS_WIDTH = 24
MAX_DETAILS_WIDTH = 64
DEFAULT_TERMINAL_WIDTH = 100


class TableReportFormatter(object):
    """Formats `ValidationResult` objects as an aligned, bordered table.

    Columns size themselves to the content, the details column wraps to fit the
    terminal, and each file's problems and notes are listed inside its row. All
    padding is computed on uncoloured text, so colour never shifts the layout.
    """

    def __init__(self, palette=None, width=None, ascii_only=False, title=None):
        self._palette = palette or Palette(False)
        self._glyphs = ASCII_BOX if ascii_only else UNICODE_BOX
        self._width = width
        self._title = title

    # -- public API ---------------------------------------------------------

    def format_report(self, results):
        if not results:
            return ["No files to validate."]

        rows = [self._build_row(result) for result in results]
        widths = self._column_widths(rows)

        lines = []
        if self._title:
            lines.extend(self._format_title(widths))
        lines.append(self._rule("tl", "top_x", "tr", widths))
        lines.append(self._header(widths))
        lines.append(self._rule("head_l", "head_x", "head_r", widths))
        for index, row in enumerate(rows):
            if index:
                lines.append(self._rule("row_l", "row_x", "row_r", widths))
            lines.extend(self._format_row(row, widths))
        lines.append(self._rule("bl", "bot_x", "br", widths))
        lines.append("")
        lines.append(self.format_summary(results))
        return lines

    def format_summary(self, results):
        total = len(results)
        flagged = [result for result in results if not result.is_valid]
        valid = total - len(flagged)
        glyphs, paint = self._glyphs, self._palette

        parts = [paint.paint(("%s %d valid" % (glyphs["ok"], valid)).strip(), "green", "bold")]
        if flagged:
            parts.append(paint.paint(
                ("%s %d flagged" % (glyphs["bad"], len(flagged))).strip(), "red", "bold"))
        parts.append(paint.dim("%d total" % total))
        summary = "   ".join(parts)

        if flagged:
            names = ", ".join(result.name for result in flagged)
            summary += "\n" + paint.red("   flagged: %s" % names)
        return summary

    # -- row construction ---------------------------------------------------

    def _build_row(self, result):
        glyphs = self._glyphs
        if result.is_valid:
            status = (("%s OK" % glyphs["ok"]).strip(), ("green", "bold"))
        else:
            status = (("%s FLAGGED" % glyphs["bad"]).strip(), ("red", "bold"))

        details = [("%s %s" % (glyphs["problem"], problem), ("red",))
                   for problem in result.problems]
        details += [("%s %s" % (glyphs["note"], note), ("yellow",)) for note in result.notes]
        if not details:
            details = [(glyphs["none"], ("grey",))]

        kind_style = ("cyan",) if result.is_valid else ("grey",)
        return {
            "status": status,
            "file": (result.name, ("bold",) if not result.is_valid else ()),
            "kind": (result.kind_label, kind_style),
            "details": details,
        }

    def _column_widths(self, rows):
        status = max([len(HEADERS[0])] + [len(row["status"][0]) for row in rows])
        name = max([len(HEADERS[1])] + [len(row["file"][0]) for row in rows])
        kind = max([len(HEADERS[2])] + [len(row["kind"][0]) for row in rows])

        terminal = self._width or shutil.get_terminal_size((DEFAULT_TERMINAL_WIDTH, 24)).columns
        # Borders and padding consume 3 characters per column, plus a trailing edge.
        overhead = 3 * len(HEADERS) + 1
        available = terminal - overhead - status - name - kind
        longest = max([len(HEADERS[3])] + [len(text) for row in rows for text, _ in row["details"]])
        details = max(MIN_DETAILS_WIDTH, min(MAX_DETAILS_WIDTH, available, longest))
        return (status, name, kind, details)

    # -- line rendering -----------------------------------------------------

    def _rule(self, left, middle, right, widths):
        glyphs = self._glyphs
        segments = [glyphs["h"] * (width + 2) for width in widths]
        return self._palette.grey(left_join(glyphs[left], glyphs[middle], glyphs[right], segments))

    def _header(self, widths):
        cells = [
            self._palette.paint(header.ljust(width), "bold")
            for header, width in zip(HEADERS, widths)
        ]
        return self._join_cells(cells)

    def _format_title(self, widths):
        inner = sum(width + 2 for width in widths) + len(widths) - 1
        text = self._truncate(" " + self._title, inner).ljust(inner)
        glyphs = self._glyphs
        return [
            self._palette.grey(glyphs["tl"] + glyphs["h"] * inner + glyphs["tr"]),
            self._palette.grey(glyphs["v"]) + self._palette.paint(text, "bold", "cyan")
            + self._palette.grey(glyphs["v"]),
            self._palette.grey(glyphs["bl"] + glyphs["h"] * inner + glyphs["br"]),
            "",
        ]

    def _format_row(self, row, widths):
        status_w, name_w, kind_w, details_w = widths

        detail_lines = []
        for text, styles in row["details"]:
            wrapped = textwrap.wrap(text, details_w, subsequent_indent="  ") or [""]
            detail_lines.extend((line, styles) for line in wrapped)

        lines = []
        for index, (text, styles) in enumerate(detail_lines):
            if index == 0:
                cells = [
                    self._cell(row["status"], status_w),
                    self._cell(row["file"], name_w),
                    self._cell(row["kind"], kind_w),
                ]
            else:
                cells = [" " * status_w, " " * name_w, " " * kind_w]
            cells.append(self._cell((text, styles), details_w))
            lines.append(self._join_cells(cells))
        return lines

    def _truncate(self, text, width):
        """Shorten `text` to `width`, marking the cut with an ellipsis."""
        if len(text) <= width:
            return text
        ellipsis = self._glyphs["ellipsis"]
        return text[:max(0, width - len(ellipsis))] + ellipsis

    def _cell(self, value, width):
        text, styles = value
        return self._palette.paint(text.ljust(width), *styles)

    def _join_cells(self, cells):
        border = self._palette.grey(self._glyphs["v"])
        return border + "".join(" %s %s" % (cell, border) for cell in cells)


def left_join(left, middle, right, segments):
    """Join pre-built horizontal segments with the given corner glyphs."""
    return left + middle.join(segments) + right
