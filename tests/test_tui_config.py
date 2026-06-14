"""Tests for tju.tui.config — config file round-trips and keyring helpers.

These tests run fully offline: config is written to a tmp directory
(via TJU_CONFIG_DIR env-var) and keyring uses an in-memory stub backend.
No Textual is needed here.
"""

from __future__ import annotations

import os
from typing import Any

import keyring
import keyring.backend
import pytest

# ---------------------------------------------------------------------------
# In-memory keyring stub
# ---------------------------------------------------------------------------


class MemoryKeyring(keyring.backend.KeyringBackend):
    """Simple in-memory keyring backend for testing."""

    priority = 10

    def __init__(self) -> None:
        self._store: dict[tuple[str, str], str] = {}

    def set_password(self, service: str, username: str, password: str) -> None:
        self._store[(service, username)] = password

    def get_password(self, service: str, username: str) -> str | None:
        return self._store.get((service, username))

    def delete_password(self, service: str, username: str) -> None:
        self._store.pop((service, username), None)


@pytest.fixture(autouse=True)
def memory_keyring(monkeypatch):
    """Replace the real OS keyring with an in-memory stub for every test."""
    backend = MemoryKeyring()
    keyring.set_keyring(backend)
    yield backend


@pytest.fixture()
def config_dir(tmp_path, monkeypatch):
    """Point TJU_CONFIG_DIR to a temporary directory."""
    monkeypatch.setenv("TJU_CONFIG_DIR", str(tmp_path))
    return tmp_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

pytest.importorskip("tju.tui.config", reason="tju[tui] extra not installed")


def test_load_config_missing(config_dir):
    """load_config returns {} when the file does not exist yet."""
    from tju.tui.config import load_config

    assert load_config() == {}


def test_save_and_load_roundtrip(config_dir):
    """Config written by save_config can be read back by load_config."""
    from tju.tui.config import load_config, save_config

    data: dict[str, Any] = {
        "credentials": {"username": "2024000001"},
        "preferences": {"default_semester": "24251"},
    }
    save_config(data)
    loaded = load_config()
    assert loaded["credentials"]["username"] == "2024000001"
    assert loaded["preferences"]["default_semester"] == "24251"


def test_config_file_permissions(config_dir):
    """Config file is written with mode 0o600 (owner read/write only)."""
    from tju.tui.config import save_config

    save_config({"credentials": {"username": "test"}})
    config_file = config_dir / "config.toml"
    assert config_file.exists()
    mode = oct(config_file.stat().st_mode)[-3:]
    assert mode == "600", f"Expected 600, got {mode}"


def test_set_and_get_username(config_dir):
    from tju.tui.config import get_username, set_username

    assert get_username() is None
    set_username("2024000001")
    assert get_username() == "2024000001"


def test_password_in_keyring_not_config(config_dir, memory_keyring):
    """Password must be stored in keyring, not written to config.toml."""
    from tju.tui.config import get_password, load_config, set_password, set_username

    set_username("2024000001")
    set_password("2024000001", "secret123")

    # Keyring should have it
    assert get_password("2024000001") == "secret123"

    # Config file must NOT contain the password
    raw_toml = (config_dir / "config.toml").read_text()
    assert "secret123" not in raw_toml


def test_delete_password(config_dir, memory_keyring):
    from tju.tui.config import delete_password, get_password, set_password

    set_password("user", "pw")
    assert get_password("user") == "pw"
    delete_password("user")
    assert get_password("user") is None


def test_delete_password_noop_if_missing(config_dir):
    """delete_password does not raise if no entry exists."""
    from tju.tui.config import delete_password

    delete_password("nonexistent")  # must not raise


def test_clear_credentials(config_dir, memory_keyring):
    from tju.tui.config import (
        clear_credentials,
        get_password,
        get_username,
        set_password,
        set_username,
    )

    set_username("2024000001")
    set_password("2024000001", "pw")
    clear_credentials()

    assert get_username() is None
    assert get_password("2024000001") is None


def test_get_preferences_default(config_dir):
    from tju.tui.config import get_preferences

    prefs = get_preferences()
    assert isinstance(prefs, dict)
    assert prefs == {}


def test_set_preference(config_dir):
    from tju.tui.config import get_preferences, set_preference

    set_preference("default_semester", "24251")
    prefs = get_preferences()
    assert prefs["default_semester"] == "24251"


def test_set_preference_preserves_existing(config_dir):
    from tju.tui.config import get_preferences, set_preference

    set_preference("default_semester", "24251")
    set_preference("campus_id", "3")
    prefs = get_preferences()
    assert prefs["default_semester"] == "24251"
    assert prefs["campus_id"] == "3"
