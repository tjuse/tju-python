# Quick Start

## Prerequisites

- Python 3.10 or later
- TJU campus network or VPN connection (`sso.tju.edu.cn` / `classes.tju.edu.cn`)
- Your TJU student credentials

## Installation

```sh
pip install tju
```

Or from source (recommended for development):

```sh
git clone https://github.com/tjuse/tju-python.git
cd tju-python
uv sync
```

## Credentials

Set your credentials as environment variables or put them in a `.env` file:

```sh
# shell
export TJU_USER=your_student_id
export TJU_PASS=your_password
```

```ini
# .env
TJU_USER=your_student_id
TJU_PASS=your_password
```

## Minimal example

```python
from tju.client import create_client

client = create_client()   # reads TJU_USER / TJU_PASS from env

# Who am I?
print(client.stu_id, client.stu_name, client.stu_type)

# Current semester code, e.g. "24252"
print(client.semester)

# Personal timetable
schedule = client.schedule()
for course in schedule:
    print(course.name, course.credit, course.campus)

# Academic scores
result = client.score()
for score in result["list"]:
    print(score.name, score.score)
```

## Error handling

All library errors inherit from one of the exceptions in `tju.exceptions`:

```python
from tju.exceptions import LoginError, DataError, HtmlParseError

try:
    client = create_client()
    schedule = client.schedule()
except LoginError:
    print("Login failed — check credentials or VPN")
except DataError as e:
    print(f"EAMS returned unexpected data: {e}")
except HtmlParseError as e:
    print(f"HTML structure changed unexpectedly: {e}")
```

## Semester codes

EAMS uses numeric semester codes.  Examples:

| Code | Meaning |
|---|---|
| `"24251"` | 2024–2025 first term |
| `"24252"` | 2024–2025 second term |
| `"25261"` | 2025–2026 first term |
| `"25262"` | 2025–2026 second term |

`client.semester` returns the current semester automatically.  The full mapping
is in `src/tju/consts.py` (`SEMESTER` dict).
