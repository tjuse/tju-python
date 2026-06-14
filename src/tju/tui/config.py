"""Backward-compatibility shim — re-exports from :mod:`tju.config`.

All credential and preference helpers now live in the top-level
:mod:`tju.config` module so they can be shared between the TUI and MCP
extras without cross-dependency.
"""

from tju.config import (  # noqa: F401
    clear_credentials,
    delete_password,
    get_password,
    get_preferences,
    get_username,
    load_config,
    save_config,
    set_password,
    set_preference,
    set_username,
)
