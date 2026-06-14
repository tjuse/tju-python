# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Interactive full-screen TUI (`tju` command, `pip install 'tju[tui]'` extra)
  for browsing profile, schedule, courses, exams, scores and free classrooms
- Local MCP server (`tju-mcp` command, `pip install 'tju[mcp]'` extra) exposing
  all read-only EAMS queries as MCP tools over stdio; compatible with Claude
  Desktop, Claude Code, and any MCP host
- Credentials stored securely: username in `~/.config/tju/config.toml`,
  password in the OS keyring (macOS Keychain / Windows Credential Manager /
  Linux Secret Service) — password never written to disk in plaintext; shared
  between the TUI and MCP server via `tju.config`
- MCP server security model: password is a hard secret — no tool accepts or
  returns it; profile PII (student ID, phone, address, email) masked by default;
  masking controlled server-side (`mcp_reveal_pii` config flag), never by a
  tool argument

## [0.1.2] - 2026-06-13

### Changed

- Migrated repository to <https://github.com/tjuse/tju-python>
- Docs site moved to custom domain <https://python.tjuse.com/>
- CI badge switched to shields.io for reliable rendering on PyPI
- Chinese README link in PyPI description now uses absolute GitHub URL (fixes 404)
- Docs deployment no longer triggered on version tags (fixes GitHub Pages
  environment protection rejection)

## [0.1.1] - 2026-06-13

### Fixed

- Set `requires-python = ">= 3.11"` — `onnxruntime` ≥ 1.24 (pulled in by `ddddocr`) no longer
  ships cp310 wheels, so Python 3.10 was never actually supported
- Updated classifiers to reflect supported versions (3.11 / 3.12 / 3.13) and CI matrix to match

## [0.1.0] - 2026-06-13

### Added

- **Session / Authentication** (`tju.Session`)
  - CAS SSO login at `sso.tju.edu.cn` with CAPTCHA solving via `ddddocr`
  - DES-encrypted password using embedded JavaScript (`tju.encrypt`)
  - Automatic session renewal when EAMS redirects back to the login page
  - `Session.logout()` implementation
  - Context-manager support (`with Session() as s:`)

- **Client** (`tju.client.Client`, `tju.client.create_client`)
  - Composable mixin architecture — one `Client` class aggregates all feature mixins
  - Identity properties: `stu_id`, `stu_name`, `stu_type` (UG/GS), `has_minor`, `semester`
  - `create_client()` factory for one-line setup

- **Student profile** (`ProfileMixin.profile`)
  - Scrapes the full EAMS personal-information page (~35 fields including enrollment dates,
    supervisors, contact details, administrative class)

- **Personal timetable** (`ScheduleMixin.schedule`)
  - Fetches the EAMS course-table for a given semester
  - Supports standard, class-level, and minor timetables
  - Auto-detects graduate vs. undergraduate project

- **Public course library** (`CourseMixin.query_courses`)
  - Paginated query of the EAMS course catalogue
  - Supports both undergraduate (project 1) and graduate (project 22) libraries
  - Handles 12-column (GS) and 16-column (UG) HTML table formats automatically

- **Course detail & syllabus** (`CourseMixin.query_course_info`, `query_syllabus`)
  - Per-course metadata (semester, faculty)
  - Syllabus HTML → Markdown conversion via `markdownify`

- **Exam schedule** (`ExamMixin.exam`)
  - Full exam timetable including date, time range, location, and seat number

- **Academic scores** (`ScoreMixin.score`, `ScoreMixin.exp_score`)
  - Undergraduate and graduate score histories with per-semester summaries
  - Experiment/lab course scores

- **Free classroom search** (`ClassroomMixin.free_classrooms`)
  - Queries available classrooms by date range, campus, building, room type, and seat count
  - Supports both class-period (小节) and clock-time search modes
  - Gracefully raises `DataError` when the EAMS period schedule is unavailable

- **Typed data models** (`tju.models`)
  - `marshmallow-dataclass` frozen dataclasses for all returned entities
  - Chinese-keyed EAMS data transparently mapped to Python field names

- **Example scripts**
  - `examples/fetch_schedule.py` — fetch personal timetable, print summary, save JSON
  - `examples/fetch_all_courses.py` — fetch full UG+GS course library (paginated), save JSON

- **Documentation**
  - Bilingual README (English `README.md` + Chinese `README.zh-CN.md`)
  - `AGENTS.md` — architecture guide and contributor conventions
  - MkDocs + Material + mkdocstrings docs site (auto-generated from docstrings)

- **CI / release automation** (GitHub Actions)
  - CI workflow: runs pytest on Python 3.10 / 3.11 / 3.12
  - Docs workflow: builds and deploys to GitHub Pages on every push to `main`
  - Publish workflow: builds sdist + wheel and publishes to PyPI via OIDC trusted
    publishing on `v*` tags; creates GitHub Release with changelog notes

### Fixed

- **Course parser robustness**
  - `parse_course` rebuilt with a dynamic column regex so the same function handles both
    the older 16-column UG format and the newer 12-column GS format without hardcoding
  - Courses with no scheduled class slots (thesis supervision, online-only) no longer cause
    `HtmlParseError`; their `arrange` is returned as an empty list

- **`query_courses` project-context bug**
  - Fresh EAMS sessions default to project 1 (UG); querying the GS project (22) without
    first setting the project context returned `AuthenticationException`.  A
    `COURSETABLE_INDEX_URL_PATH` pre-flight request is now issued before every library query

### Changed

- Migrated project tooling from **rye** to **uv** (`[dependency-groups]` in `pyproject.toml`)
- Schema system refactored to use `LoadDumpSchema` base with `post_dump` key restoration,
  enabling clean Python-named serialised output from Chinese-keyed EAMS data

[Unreleased]: https://github.com/tjuse/tju-python/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/tjuse/tju-python/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/tjuse/tju-python/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/tjuse/tju-python/releases/tag/v0.1.0
