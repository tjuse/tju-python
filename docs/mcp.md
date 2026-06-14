# MCP Server

`tju` ships an optional local **MCP server** (`tju-mcp`) so you can query your
TJU academic data from any AI agent that supports the
[Model Context Protocol](https://modelcontextprotocol.io/) — including Claude
Desktop, Claude Code, and other MCP hosts.

## Confidentiality guarantee

> **Your password is never exposed to the AI agent — by design, not by
> configuration.**

The MCP server acts as the **credential boundary**:

- The server reads your username and password from the **OS keyring** (macOS
  Keychain / Windows Credential Manager / Linux Secret Service) at startup.
- It logs into TJU SSO on your behalf and caches the session **inside the server
  process**.
- **No tool accepts a username or password parameter.**  No tool ever returns a
  password.  Even a fully compromised agent cannot obtain your credentials,
  because they are not on any tool surface.
- Transport is **stdio only** — the host launches the server as a local
  subprocess; no network port is opened, no auth surface is exposed.

Profile PII (student ID, phone, home address, email…) is **masked by default**.
See [PII masking](#pii-masking) for details.

## Installation

```sh
pip install 'tju[mcp]'
```

Or with uv:

```sh
uv pip install 'tju[mcp]'
```

## One-time credential setup

Run the setup wizard once to store your credentials in the OS keyring:

```sh
tju-mcp setup
```

You will be prompted for your student ID and password.  The password is stored
in the OS keyring and **never written to disk in plaintext**.

Alternatively, if you have already logged in via the [TUI](tui.md), the same
credentials are used automatically.

## Claude Desktop configuration

Add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tju": {
      "command": "tju-mcp"
    }
  }
}
```

No secrets go in the config file.  The server reads them from the keyring.

!!! note "Network requirement"
    All data-fetching tools require a connection to the TJU campus network or
    VPN (`sso.tju.edu.cn` / `classes.tju.edu.cn`) — the same constraint as the
    Python library.

## Available tools

| Tool | Description |
|---|---|
| `whoami` | Name, student type, current semester (student ID masked by default) |
| `get_profile` | Full student profile (~35 fields, PII masked by default) |
| `get_schedule` | Personal timetable for a given semester |
| `get_exam` | Exam schedule for a given semester |
| `get_scores` | Full score history (UG/GS auto-detected) |
| `get_exp_scores` | Experiment/lab scores for a given semester |
| `query_courses` | Public course library (UG or GS) |
| `get_course_info` | Course metadata by lesson ID |
| `get_syllabus` | Course syllabus as Markdown |
| `search_free_classrooms` | Available classrooms by date, campus, and period |

All tools are **read-only** — there are no enrollment, registration, or
write-operation tools.

## PII masking

By default, the following profile fields are partially masked (e.g.
`2024****01`):

- Student ID (`stu_id`)
- Email, phone, mobile, home phone
- Home address and zip code
- Contact address

To receive unmasked values, set the flag **on the server** (never via a tool
argument, so the agent cannot flip it):

=== "config.toml"

    ```toml
    # ~/.config/tju/config.toml
    [preferences]
    mcp_reveal_pii = true
    ```

=== "Environment variable"

    ```sh
    TJU_MCP_REVEAL_PII=1 tju-mcp
    ```

## Semester codes

EAMS uses a 5-digit semester code: `YYYX1` (first term) or `YYYX2` (second
term), where `YYY` is the two-digit academic year.

| Code | Period |
|---|---|
| `24251` | 2024–2025 first term (autumn) |
| `24252` | 2024–2025 second term (spring) |

## Clearing saved credentials

```sh
tju-mcp setup   # re-enter to overwrite
```

Or from Python:

```python
from tju.config import clear_credentials
clear_credentials()
```

## Launching manually (for debugging)

```sh
tju-mcp          # stdio server (attach via MCP Inspector or Claude Desktop)
python -m tju.mcp
```

Inspect the server with the official MCP Inspector:

```sh
npx @modelcontextprotocol/inspector tju-mcp
```
