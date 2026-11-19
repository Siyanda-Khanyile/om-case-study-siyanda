"""ANSI colour handling, with graceful degradation."""

import os


class Palette(object):
    """Wraps text in ANSI colour codes when the output supports them.

    When disabled every method returns its argument unchanged, so the same
    formatting code produces clean text for pipes, files and CI logs.
    """

    RESET = "\033[0m"
    CODES = {
        "bold": "\033[1m",
        "dim": "\033[2m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "cyan": "\033[36m",
        "grey": "\033[90m",
    }

    def __init__(self, enabled=True):
        self.enabled = bool(enabled)

    @classmethod
    def for_stream(cls, stream, force=None):
        """Enable colour only for a real terminal, unless `force` overrides.

        Honours the NO_COLOR convention and `TERM=dumb`.
        """
        if force is not None:
            return cls(force)
        if os.environ.get("NO_COLOR") is not None:
            return cls(False)
        if os.environ.get("TERM") == "dumb":
            return cls(False)
        return cls(bool(getattr(stream, "isatty", lambda: False)()))

    def paint(self, text, *styles):
        if not self.enabled or not styles:
            return text
        prefix = "".join(self.CODES[style] for style in styles if style in self.CODES)
        return "%s%s%s" % (prefix, text, self.RESET) if prefix else text

    def __getattr__(self, name):
        if name in self.CODES:
            return lambda text: self.paint(text, name)
        raise AttributeError(name)
