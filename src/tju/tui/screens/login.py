"""Login screen — collects username / password and establishes a session."""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label, LoadingIndicator, Static

from tju import Session
from tju.client import Client
from tju.exceptions import LoginError, SessionError

from .. import config as cfg


class LoginScreen(Screen):
    """Full-screen login form.

    On success the session and client are stored on the app and the main
    screen is pushed.
    """

    def compose(self) -> ComposeResult:
        # Use Vertical (a real layout container) instead of Static
        with Vertical(id="login-box"):
            yield Static("TJU", id="login-title")
            yield Static("Tianjin University Client", id="login-subtitle")
            yield Label("学号 / 用户名")
            yield Input(
                placeholder="2024xxxxxx",
                id="input-username",
                value=cfg.get_username() or "",
            )
            yield Label("密码")
            yield Input(
                placeholder="••••••••",
                id="input-password",
                password=True,
            )
            yield Button("登 录", variant="primary", id="btn-login")
            yield LoadingIndicator(id="loading")
            yield Static("", id="login-error")

    def on_mount(self) -> None:
        self.query_one("#loading", LoadingIndicator).display = False
        username_input = self.query_one("#input-username", Input)
        if username_input.value:
            self.query_one("#input-password", Input).focus()
        else:
            username_input.focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-login":
            self._do_login()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "input-username":
            self.query_one("#input-password", Input).focus()
        elif event.input.id == "input-password":
            self._do_login()

    def _do_login(self) -> None:
        username = self.query_one("#input-username", Input).value.strip()
        password = self.query_one("#input-password", Input).value
        if not username or not password:
            self._show_error("请填写学号和密码")
            return
        self._set_loading(True)
        self._login_worker(username, password)

    @work(thread=True)
    def _login_worker(self, username: str, password: str) -> None:
        """Blocking login on a background thread (httpx + ddddocr)."""
        try:
            session = Session(username=username, password=password)
            session.login()
            client = Client(session=session)
        except (LoginError, SessionError) as exc:
            self.app.call_from_thread(self._on_login_error, str(exc))
            return
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(
                self._on_login_error, f"未知错误: {exc}"
            )
            return
        self.app.call_from_thread(self._on_login_success, username, password, client)

    def _on_login_success(
        self, username: str, password: str, client: Client
    ) -> None:
        # Persist credentials
        cfg.set_username(username)
        cfg.set_password(username, password)

        # Store on app for MainScreen to access
        self.app.client = client  # type: ignore[attr-defined]

        self._set_loading(False)
        from .main import MainScreen  # noqa: PLC0415

        self.app.push_screen(MainScreen())

    def _on_login_error(self, message: str) -> None:
        self._set_loading(False)
        self._show_error(message)

    def _set_loading(self, loading: bool) -> None:
        btn = self.query_one("#btn-login", Button)
        loading_widget = self.query_one("#loading", LoadingIndicator)
        btn.disabled = loading
        loading_widget.display = loading

    def _show_error(self, message: str) -> None:
        error_widget = self.query_one("#login-error", Static)
        error_widget.update(f"⚠ {message}")
        error_widget.add_class("visible")
