<p align="center"><b>TJU</b> <sup><samp>The Python TJU client</samp></sup></p>

[![PyPI version](https://img.shields.io/pypi/v/tju.svg)](https://pypi.org/project/tju/)

English | [简体中文](README.zh-CN.md)

> **Work in progress.** The API is functional but not yet stable.

`tju` is a Python library that logs into Tianjin University's SSO and EAMS systems and returns structured academic data. It handles CAS authentication, CAPTCHA solving (via `ddddocr`), and HTML parsing — so your code just calls methods and gets typed objects back.

> **Network requirement:** All live API calls require an active connection to the TJU campus network or VPN (`sso.tju.edu.cn` / `classes.tju.edu.cn`).

## Features

| Feature | Client method |
|---|---|
| Student profile | `client.profile` |
| Personal timetable | `client.schedule(semester)` |
| Public course library | `client.query_courses(semester)` |
| Course detail | `client.query_course_info(lession_id)` |
| Course syllabus | `client.query_syllabus(lession_id)` |
| Exam schedule | `client.exam(semester)` |
| Scores (UG + GS) | `client.score()` |
| Experiment scores | `client.exp_score(semester)` |
| Free classroom search | `client.free_classrooms(date_begin, ...)` |

## Installation

```sh
pip install tju
```

From source (recommended for development):

```sh
git clone https://github.com/superpung/tju-python.git
cd tju-python
uv sync       # installs all dependencies into .venv
```

## Quick start

Set your credentials as environment variables (or put them in a `.env` file):

```sh
export TJU_USER=your_student_id
export TJU_PASS=your_password
```

```python
from tju.client import create_client

client = create_client()   # reads TJU_USER / TJU_PASS from env
print(client.profile)
print(client.schedule(semester="24251"))
```

**Runnable example — fetch and save the current timetable:**

```sh
uv run --env-file .env python examples/fetch_schedule.py
```

The script prints a human-readable course list and writes the full JSON to
`examples/output/schedule_<semester>.json`.

## Usage

```python
from tju import Session
from tju.client import Client

session = Session()                              # or: Session(username=..., password=...)
client  = Client(session=session)

# Identity
client.stu_id        # student ID string
client.stu_name      # name string
client.stu_type      # StuType.UNDERGRADUATE | StuType.GRADUATE
client.has_minor     # bool
client.semester      # current semester code, e.g. "24252"

# Data
client.profile
client.schedule(semester="24251")
client.query_courses(semester="24251")
client.query_course_info(lession_id="387248")
client.query_syllabus(lession_id="387248")
client.exam(semester="24251")
client.score()
client.exp_score(semester="20211")
client.free_classrooms(date_begin="2025-10-08", campus_id=3)
```

Semester codes follow the EAMS convention, e.g. `"24251"` = 2024–2025 first term,
`"24252"` = 2024–2025 second term. See `src/tju/consts.py` for the full `SEMESTER` map.

## Development

```sh
uv sync          # install runtime + dev dependencies
uv run pytest    # run the offline test suite (30 tests, no network required)
```

See [AGENTS.md](AGENTS.md) for architecture details and contributor guidance.

## License

[GPLv3 License](LICENSE) © 2023-PRESENT Super Lee
