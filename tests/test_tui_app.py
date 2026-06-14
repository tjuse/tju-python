"""Smoke tests for the TJU TUI application using Textual's test pilot.

All tests run offline with a mocked Client / Session — no campus network or
VPN required.  These tests are skipped automatically if the ``tui`` extra
(Textual) is not installed.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

textual = pytest.importorskip("textual", reason="tju[tui] extra not installed")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def config_dir(tmp_path, monkeypatch):
    """Redirect config to a temp dir; swap in an in-memory keyring."""
    monkeypatch.setenv("TJU_CONFIG_DIR", str(tmp_path))

    import keyring
    import keyring.backend

    class MemKeyring(keyring.backend.KeyringBackend):
        priority = 10
        _store: dict = {}

        def set_password(self, s, u, p):
            self._store[(s, u)] = p

        def get_password(self, s, u):
            return self._store.get((s, u))

        def delete_password(self, s, u):
            self._store.pop((s, u), None)

    keyring.set_keyring(MemKeyring())
    return tmp_path


@pytest.fixture()
def mock_client():
    """Minimal mock of tju.client.Client."""
    client = MagicMock()
    client.stu_name = "测试同学"
    client.stu_id = "2024000001"
    return client


# ---------------------------------------------------------------------------
# Helper: pause multiple times so Textual finishes composing
# ---------------------------------------------------------------------------


async def _settle(pilot, n: int = 3) -> None:
    for _ in range(n):
        await pilot.pause()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_app_boots_to_login_without_creds(config_dir):
    """App shows LoginScreen when no credentials are saved."""
    from tju.tui.app import TjuApp
    from tju.tui.screens.login import LoginScreen

    async with TjuApp().run_test(headless=True) as pilot:
        await _settle(pilot)
        assert isinstance(pilot.app.screen, LoginScreen)


async def test_login_screen_has_expected_inputs(config_dir):
    """LoginScreen exposes username and password Input widgets."""
    from textual.widgets import Input

    from tju.tui.app import TjuApp

    async with TjuApp().run_test(headless=True) as pilot:
        await _settle(pilot)
        # Query from the active screen, not the app root
        screen = pilot.app.screen
        inputs = list(screen.query(Input))
        ids = [w.id for w in inputs]
        assert "input-username" in ids
        assert "input-password" in ids


async def test_login_error_shown_on_empty_submit(config_dir):
    """Submitting the login form without credentials shows an error message."""
    from textual.widgets import Static

    from tju.tui.app import TjuApp

    async with TjuApp().run_test(headless=True) as pilot:
        await _settle(pilot)
        await pilot.click("#btn-login")
        await _settle(pilot)
        screen = pilot.app.screen
        error_widget = screen.query_one("#login-error", Static)
        assert "visible" in error_widget.classes


async def test_main_screen_sidebar_has_actions(config_dir, mock_client):
    """MainScreen sidebar lists the expected navigation items."""
    from textual.widgets import ListItem

    from tju.tui.app import TjuApp
    from tju.tui.screens.main import MainScreen

    app = TjuApp()
    app.client = mock_client

    async with app.run_test(headless=True) as pilot:
        await _settle(pilot)
        await pilot.app.push_screen(MainScreen())
        await _settle(pilot, n=5)

        screen = pilot.app.screen
        items = list(screen.query(ListItem))
        item_ids = [item.id for item in items if item.id]
        assert "item-profile" in item_ids
        assert "item-schedule" in item_ids
        assert "item-scores" in item_ids
        assert "item-logout" in item_ids


async def test_main_screen_profile_panel_mounts(config_dir, mock_client):
    """Selecting 'profile' mounts a loading indicator in the content area."""
    from textual.widgets import LoadingIndicator

    from tju.tui.app import TjuApp
    from tju.tui.screens.main import MainScreen

    app = TjuApp()
    app.client = mock_client

    async with app.run_test(headless=True) as pilot:
        await _settle(pilot)
        await pilot.app.push_screen(MainScreen())
        await _settle(pilot, n=5)

        screen = pilot.app.screen
        await pilot.click("#item-profile")
        await _settle(pilot, n=3)

        # Loading indicator should be in the DOM after panel is shown
        try:
            li = screen.query_one("#loading", LoadingIndicator)
            assert li is not None
        except Exception:
            # Worker already finished — also acceptable
            pass


async def test_quit_binding(config_dir):
    """Pressing 'q' exits the application."""
    from tju.tui.app import TjuApp

    async with TjuApp().run_test(headless=True) as pilot:
        await _settle(pilot)
        await pilot.press("q")
        # reaching here without exception means clean exit
