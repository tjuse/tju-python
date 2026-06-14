"""Local configuration and credential storage for the TJU client.

Config file (plaintext, chmod 0o600):
    ``<user_config_dir>/tju/config.toml``

Schema::

    [credentials]
    username = "2024000001"

    [preferences]
    default_semester = "24251"   # optional
    mcp_reveal_pii   = false     # optional — expose PII in MCP tools (default: false)

Password: stored in the OS keyring (macOS Keychain / Windows Credential
Manager / Linux Secret Service) via the ``keyring`` library.  The password
is **never** written to disk in plaintext.
"""

from __future__ import annotations

import os
import stat
import tomllib
from pathlib import Path
from typing import Any

import keyring
import platformdirs
import tomli_w

_SERVICE = "tju"
_APP = "tju"


def _config_path() -> Path:
    """Return the path to ``config.toml``, honouring ``TJU_CONFIG_DIR``
    if set (useful for tests)."""
    env_dir = os.environ.get("TJU_CONFIG_DIR")
    if env_dir:
        return Path(env_dir) / "config.toml"
    return Path(platformdirs.user_config_dir(_APP)) / "config.toml"


def load_config() -> dict[str, Any]:
    """Load and return the config dict.  Returns ``{}`` if the file does not
    exist yet."""
    path = _config_path()
    if not path.exists():
        return {}
    with open(path, "rb") as fh:
        return tomllib.load(fh)


def save_config(cfg: dict[str, Any]) -> None:
    """Persist *cfg* to the config file (mode ``0o600``)."""
    path = _config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as fh:
        tomli_w.dump(cfg, fh)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)


# ---------------------------------------------------------------------------
# Credential helpers
# ---------------------------------------------------------------------------


def get_username(cfg: dict[str, Any] | None = None) -> str | None:
    """Return the stored username from *cfg* (loads from disk if not given)."""
    if cfg is None:
        cfg = load_config()
    return cfg.get("credentials", {}).get("username")


def set_username(username: str, cfg: dict[str, Any] | None = None) -> None:
    """Persist *username* to the config file."""
    if cfg is None:
        cfg = load_config()
    cfg.setdefault("credentials", {})["username"] = username
    save_config(cfg)


def get_password(username: str) -> str | None:
    """Retrieve the password for *username* from the OS keyring.

    Returns ``None`` if no credential is stored, or if no usable keyring
    backend is available on the system (so callers degrade gracefully rather
    than crashing — e.g. auto-login is simply skipped).
    """
    try:
        return keyring.get_password(_SERVICE, username)
    except keyring.errors.KeyringError:
        return None


def set_password(username: str, password: str) -> bool:
    """Store *password* in the OS keyring under *username*.

    Returns ``True`` on success, ``False`` if no usable keyring backend is
    available (the caller may then warn the user that the credential could not
    be remembered for next time).
    """
    try:
        keyring.set_password(_SERVICE, username, password)
        return True
    except keyring.errors.KeyringError:
        return False


def delete_password(username: str) -> None:
    """Remove the keyring entry for *username* (no-op if absent or no backend)."""
    try:
        keyring.delete_password(_SERVICE, username)
    except keyring.errors.KeyringError:
        pass


def clear_credentials() -> None:
    """Remove username from config and password from the keyring."""
    cfg = load_config()
    username = get_username(cfg)
    if username:
        delete_password(username)
    cfg.pop("credentials", None)
    save_config(cfg)


# ---------------------------------------------------------------------------
# Preferences helpers
# ---------------------------------------------------------------------------


def get_preferences(cfg: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return the ``[preferences]`` section (or an empty dict)."""
    if cfg is None:
        cfg = load_config()
    return dict(cfg.get("preferences", {}))


def set_preference(key: str, value: Any) -> None:
    """Set a single preference key and persist."""
    cfg = load_config()
    cfg.setdefault("preferences", {})[key] = value
    save_config(cfg)
