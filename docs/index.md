# tju

**Python client for Tianjin University's SSO and EAMS systems.**

[![PyPI version](https://img.shields.io/pypi/v/tju.svg)](https://pypi.org/project/tju/)
[![CI](https://img.shields.io/github/actions/workflow/status/tjuse/tju-python/ci.yml?branch=main&label=CI)](https://github.com/tjuse/tju-python/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://github.com/tjuse/tju-python/blob/main/LICENSE)

> **Beta.** The API is functional; minor breaking changes may occur before v1.0.

`tju` is a Python library that logs into TJU's SSO and EAMS systems and returns structured academic data.
It handles CAS authentication, CAPTCHA solving (via `ddddocr`), and HTML parsing — so your code just calls methods and gets typed objects back.

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

## Quick start

```python
from tju.client import create_client

client = create_client()   # reads TJU_USER / TJU_PASS from env
print(client.profile)
print(client.schedule())
```

See the [Quick Start](quickstart.md) page for full details and the [Examples](examples.md) page
for runnable scripts.

## License

[GPLv3](https://github.com/tjuse/tju-python/blob/main/LICENSE) © 2023-PRESENT Super Lee
