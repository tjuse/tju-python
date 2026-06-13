# Contributing

Thank you for your interest in `tju`!

## Development setup

```sh
git clone https://github.com/superpung/tju-python.git
cd tju-python
uv sync          # installs runtime + dev deps into .venv
```

## Running tests

The test suite is fully **offline** — no network access or credentials required.

```sh
uv run pytest -v
```

30 tests across three modules:

| File | What it tests |
|---|---|
| `tests/test_parser.py` | Parser functions: raw HTML → dict/markdown |
| `tests/test_schema.py` | Model load/dump: parsed dict → typed dataclass → JSON |
| `tests/test_encrypt.py` | DES `strEnc` encryption |

## Adding a feature

Follow the four-layer pipeline:

```
Session  →  Client mixin  →  parser function  →  model dataclass
```

1. **Parser** (`src/tju/parser/<feature>.py`) — pure function: `html: str → dict | list`.
   No network I/O. Export it from `src/tju/parser/__init__.py`.
2. **Model** (`src/tju/models/<feature>.py`) — `marshmallow-dataclass` frozen dataclass.
   Use `mfield(data_key="中文字段名")` to map Chinese column headers. Export from
   `src/tju/models/__init__.py`.
3. **Mixin** (`src/tju/client/api/<feature>.py`) — `class XMixin(BaseClient)` with one or
   more methods that orchestrate HTTP calls and call the parser + model. Export from
   `src/tju/client/api/__init__.py` and add to the `Client` base-class list in
   `src/tju/client/__init__.py`.
4. **Tests + fixtures** — add `tests/resources/website/<feature>.html` (sanitised real HTML),
   `tests/resources/parsed/parsed_<feature>.json`, and
   `tests/resources/serialised/<feature>.json`, then add test functions in
   `tests/test_parser.py` and `tests/test_schema.py`.

## Fixture privacy rule

Real personal data lives **only** in the gitignored `.scratch/` directory.
Every committed fixture must be **sanitised**: replace real names, student IDs, national IDs,
photos, and grades with structurally-valid fake placeholders before adding to git.

## Docstrings

Use a short, terse style (one-liner for simple functions, Google-style for complex ones).
All public classes and functions should have at least a one-line docstring so that
the MkDocs API reference is complete.

## Building docs locally

```sh
uv sync --group docs
uv run mkdocs serve     # live-reload at http://127.0.0.1:8000
```

## Code style

There is currently no linting or type-checking configuration.  Match the style of
surrounding code: same comment density, naming, and idiom.
