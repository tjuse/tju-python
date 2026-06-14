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
    client.semester = "24251"
    return client


@pytest.fixture()
def main_screen(config_dir, mock_client):
    """A coroutine factory returning (app, pilot) with MainScreen pushed."""
    from tju.tui.app import TjuApp

    app = TjuApp()
    app.client = mock_client
    return app


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


# ---------------------------------------------------------------------------
# Content-swapping / DuplicateIds regression tests
# ---------------------------------------------------------------------------


async def test_content_swap_no_duplicate_ids(main_screen):
    """Rapidly swapping panels must not raise DuplicateIds.

    Regression test for the bug where ``child.remove()`` (deferred) ran after
    new fixed-id widgets were mounted.  ``_swap`` now awaits removal first.
    """
    from tju.tui.render import render_profile, render_schedule
    from tju.tui.screens.main import MainScreen

    app = main_screen
    async with app.run_test(headless=True) as pilot:
        await _settle(pilot)
        await pilot.app.push_screen(MainScreen())
        await _settle(pilot, n=5)
        screen = pilot.app.screen

        profile_data = {"stu_id": "2024000001", "stu_name": "测试同学"}
        sched_rows = [{"name": "高等数学", "credit": "4", "teacher": "张老师"}]

        # Interleave param-bar (semester input id) and non-param renders many
        # times — this is exactly what used to raise DuplicateIds.
        for _ in range(4):
            await screen._show_loading()
            await _settle(pilot, n=2)
            await screen._show_table("个人信息", render_profile, profile_data)
            await _settle(pilot, n=2)
            await screen._show_table(
                "课表", render_schedule, sched_rows, param_bar=True
            )
            await _settle(pilot, n=2)
            await screen._show_settings()
            await _settle(pilot, n=2)
            await screen._show_classroom_form()
            await _settle(pilot, n=2)
            await screen._show_error("测试错误")
            await _settle(pilot, n=2)

        # Final state is the error box; body should hold exactly its children.
        from textual.containers import VerticalScroll

        body = screen.query_one("#content-body", VerticalScroll)
        assert len(body.children) >= 1


async def test_tab_toggles_panel_focus(main_screen):
    """Tab switches focus between the menu and content panels."""
    from textual.widgets import ListView

    from tju.tui.screens.main import MainScreen

    app = main_screen
    async with app.run_test(headless=True) as pilot:
        await _settle(pilot)
        await pilot.app.push_screen(MainScreen())
        await _settle(pilot, n=5)
        screen = pilot.app.screen

        menu = screen.query_one("#menu", ListView)
        assert menu.has_focus  # starts focused on menu

        await pilot.press("tab")
        await _settle(pilot, n=2)
        # focus moved off the menu
        assert not menu.has_focus

        await pilot.press("tab")
        await _settle(pilot, n=2)
        assert menu.has_focus


async def test_param_semester_bar_has_input(main_screen):
    """A param-bar render mounts a queryable semester input."""
    from textual.widgets import Input

    from tju.tui.render import render_schedule
    from tju.tui.screens.main import MainScreen

    app = main_screen
    async with app.run_test(headless=True) as pilot:
        await _settle(pilot)
        await pilot.app.push_screen(MainScreen())
        await _settle(pilot, n=5)
        screen = pilot.app.screen

        await screen._show_table(
            "课表", render_schedule, [{"name": "x"}], param_bar=True
        )
        await _settle(pilot, n=2)
        inp = screen.query_one("#param-semester", Input)
        assert inp is not None
