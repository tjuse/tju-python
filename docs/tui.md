# Interactive TUI

`tju` ships an optional full-screen terminal application so you can browse
your academic data without writing any Python.

## Installation

The TUI requires extra dependencies (Textual, keyring, platformdirs):

```sh
pip install 'tju[tui]'
```

Or with uv:

```sh
uv pip install 'tju[tui]'
```

## Launching

```sh
tju
```

Or:

```sh
python -m tju.tui
```

The app opens in your terminal. A campus network connection or VPN
(`sso.tju.edu.cn` / `classes.tju.edu.cn`) is required for all data fetching —
same as using the library directly.

## First login

Enter your student ID and password. On success the TUI saves:

- **Username** in a plaintext config file (mode `0o600`) at:
  - macOS / Linux: `~/.config/tju/config.toml`
  - Windows: `%APPDATA%\tju\config.toml`
- **Password** in the **OS keyring** (macOS Keychain, Windows Credential
  Manager, Linux Secret Service via `keyring`). The password is never
  written to disk in plaintext.

Subsequent launches auto-login using the saved credentials.

## Layout

The interface uses a **lazygit / nvim-style two-pane layout**: a navigation
**menu** panel on the left and a **content** panel on the right.  The active
panel is highlighted with an accent border that follows keyboard focus.

Navigate with the menu on the left:

| Menu item    | Description |
|---|---|
| 个人信息  | Full student profile (every non-empty field) |
| 课表      | Personal timetable (defaults to current semester) |
| 成绩      | Full score history (UG or GS, auto-detected) |
| 考试安排  | Exam schedule (defaults to current semester) |
| 实验成绩  | Experiment/lab scores for a given semester |
| 课程库    | Public course library (UG + GS) |
| 空闲教室  | Free-classroom search by date and period |
| 设置      | Preferences (default semester) |
| 退出登录  | Clear saved credentials and return to login |

Selecting a data item loads it immediately.  For the semester-based views
(课表 / 考试安排 / 实验成绩) a small input bar lets you type a different
semester code and press **Enter** to refetch.

## Keyboard shortcuts

| Key | Action |
|---|---|
| `j` / `k` (or `↑` / `↓`) | Move up/down in the menu or table |
| `Enter` | Open the highlighted menu item |
| `Tab` | Switch focus between the menu and content panels |
| `r` | Refresh the current view |
| `g` / `G` | Jump to the top / bottom of a table |
| `q` | Quit the application |
| `?` | Show keyboard shortcuts |

## Clearing saved credentials

From inside the TUI: choose **退出登录** (Logout) in the sidebar.

From the shell:

```python
from tju.config import clear_credentials
clear_credentials()
```

This removes the username from `config.toml` and deletes the keyring entry.

## Uninstalling the TUI extra

The TUI extra can be removed without affecting the core `tju` library:

```sh
pip uninstall textual keyring platformdirs tomli-w
```
