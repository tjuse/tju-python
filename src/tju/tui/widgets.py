"""Small widget subclasses adding vim-style (j/k) navigation."""

from __future__ import annotations

from textual.binding import Binding
from textual.widgets import DataTable, ListView


class VimListView(ListView):
    """A :class:`ListView` that also moves with ``j`` / ``k``."""

    BINDINGS = [
        Binding("j", "cursor_down", "下", show=False),
        Binding("k", "cursor_up", "上", show=False),
    ]


class VimDataTable(DataTable):
    """A :class:`DataTable` that also scrolls with ``j`` / ``k`` / ``g`` / ``G``."""

    BINDINGS = [
        Binding("j", "cursor_down", "下", show=False),
        Binding("k", "cursor_up", "上", show=False),
        Binding("g", "scroll_top", "顶部", show=False),
        Binding("G", "scroll_bottom", "底部", show=False),
    ]
