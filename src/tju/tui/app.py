"""Root Textual application class for the TJU TUI."""

from __future__ import annotations

from textual.app import App
from textual.binding import Binding

from tju.client import Client

from . import config as cfg
from .screens import LoginScreen, MainScreen


class TjuApp(App):
    """Full-screen TUI for Tianjin University's EAMS client.

    Starts at :class:`~tju.tui.screens.LoginScreen` unless saved credentials
    are found in the config file and OS keyring, in which case it re-uses the
    stored credentials to log in automatically.
    """

    TITLE = "TJU"
    CSS_PATH = "app.tcss"
    BINDINGS = [
        Binding("q", "quit", "退出", show=True),
        Binding("question_mark", "show_help", "帮助", show=True),
    ]

    # The active Client is stored here so screens can access it without
    # passing it around explicitly.
    client: Client | None = None

    def on_mount(self) -> None:
        username = cfg.get_username()
        if username:
            password = cfg.get_password(username)
            if password:
                # Auto-login: push the login screen which will handle it
                login = LoginScreen()
                self.push_screen(login)
                # Pre-fill and trigger auto-login after a short delay so the
                # screen has time to compose
                self.set_timer(0.1, lambda: self._auto_login(login, username, password))
                return
        self.push_screen(LoginScreen())

    def _auto_login(
        self, login: LoginScreen, username: str, password: str
    ) -> None:
        """Trigger login with stored credentials (called once screen is ready)."""
        from textual.widgets import Input  # noqa: PLC0415

        try:
            login.query_one("#input-username", Input).value = username
            login.query_one("#input-password", Input).value = password
        except Exception:  # noqa: BLE001
            return
        login._do_login()

    def action_show_help(self) -> None:
        self.notify(
            "q — 退出  |  ← 侧边栏选择功能",
            title="快捷键",
            timeout=5,
        )
