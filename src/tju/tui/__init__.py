"""tju TUI — interactive terminal application.

Entry point for the ``tju`` console script.  Textual (and the rest of the
``tui`` optional-extra) is imported lazily so that the base library stays
usable without the extra installed.
"""

from __future__ import annotations

import sys


def main() -> None:
    """Launch the full-screen TUI.

    Prints a friendly hint and exits with status 1 if the ``tui`` extra is not
    installed (i.e. Textual is missing).
    """
    try:
        from .app import TjuApp  # noqa: PLC0415
    except ImportError:
        print(
            "The TUI extra is not installed.\n"
            "Run:  pip install 'tju[tui]'",
            file=sys.stderr,
        )
        sys.exit(1)

    TjuApp().run()
