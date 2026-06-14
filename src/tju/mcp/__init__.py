"""tju MCP server — exposes TJU EAMS queries as MCP tools.

Entry point for the ``tju-mcp`` console script.

Sub-commands
------------
``tju-mcp``          Start the MCP server (stdio transport).
``tju-mcp setup``    Store credentials in the OS keyring interactively.

The MCP SDK (``mcp``) is imported lazily so that the base library remains
usable without the ``tju[mcp]`` extra installed.
"""

from __future__ import annotations

import sys


def main(argv: list[str] | None = None) -> None:
    """Dispatch ``tju-mcp [setup|serve]``."""
    args = argv if argv is not None else sys.argv[1:]

    if args and args[0] == "setup":
        _setup()
    else:
        _serve()


def _setup() -> None:
    """Interactively prompt for credentials and store them in the keyring."""
    import getpass

    # tju.config does NOT depend on the mcp SDK — safe to import unconditionally.
    try:
        import tju.config as cfg  # noqa: PLC0415
    except ImportError as exc:
        print(f"Error importing tju.config: {exc}", file=sys.stderr)
        sys.exit(1)

    print("TJU MCP Setup — store credentials in the OS keyring")
    print("(The password is never written to disk in plaintext.)\n")

    username = input("Student ID / username: ").strip()
    if not username:
        print("Username cannot be empty.", file=sys.stderr)
        sys.exit(1)

    password = getpass.getpass("Password: ")
    if not password:
        print("Password cannot be empty.", file=sys.stderr)
        sys.exit(1)

    cfg.set_username(username)
    cfg.set_password(username, password)
    print(f"\n✓ Credentials saved for user '{username}'.")
    print("You can now start the MCP server with:  tju-mcp")


def _serve() -> None:
    """Start the MCP server over stdio."""
    try:
        from .server import build_server  # noqa: PLC0415
    except ImportError:
        print(
            "The MCP extra is not installed.\n"
            "Run:  pip install 'tju[mcp]'",
            file=sys.stderr,
        )
        sys.exit(1)

    build_server().run()
