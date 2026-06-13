"""Fetch and save the personal timetable for the current semester.

Run:
    uv run --env-file .env python examples/fetch_schedule.py

Requires TJU_USER and TJU_PASS to be set (env vars or .env file) and an
active campus network connection or VPN.  The full schedule is written to
examples/output/schedule_<semester>.json; a human-readable summary is
printed to the console.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Allow running the script from the repo root without an editable install.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tju import Session
from tju.client import Client
from tju.exceptions import DataError, HtmlParseError, LoginError
from tju.models.schedule import Course

WEEKDAYS = ["一", "二", "三", "四", "五", "六", "日"]


def _weekday_label(n: int | None) -> str:
    if n is None:
        return "?"
    try:
        return f"周{WEEKDAYS[n - 1]}"
    except IndexError:
        return f"周{n}"


def print_schedule(client: Client, semester: str) -> None:
    """Print a human-readable summary of the current timetable."""
    print(f"\n{'=' * 60}")
    print(f"  学生: {client.stu_name}  ({client.stu_id})")
    print(f"  类型: {client.stu_type.name}")
    print(f"  学期: {semester}")
    print(f"{'=' * 60}")

    schedule = client.schedule(semester=semester)
    print(f"\n共 {len(schedule)} 门课程:\n")

    for i, course in enumerate(schedule, 1):
        credit_str = f"{course.credit:.1f}" if course.credit is not None else "?"
        print(f"  [{i:2d}] {course.name or '?'}  ({credit_str} 学分)")
        print(f"       课号: {course.course_id or '?'}  班级: {course.class_id or '?'}")
        print(f"       校区: {course.campus or '?'}  周次: {course.weeks or '?'}")

        if course.arrange:
            for arr in course.arrange:
                teachers = "、".join(arr.teacher) if arr.teacher else "?"
                units = (
                    f"第 {arr.unit[0]}~{arr.unit[-1]} 节"
                    if arr.unit
                    else "?"
                )
                print(
                    f"       上课: {_weekday_label(arr.weekday)} "
                    f"{units}  {arr.location or '?'}  [{teachers}]"
                )
        print()

    return schedule


def save_schedule(schedule, semester: str) -> Path:
    """Serialize schedule to JSON and write to examples/output/."""
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"schedule_{semester}.json"

    data = Course.Schema(many=True).dump(schedule)
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out_path


if __name__ == "__main__":
    try:
        session = Session()
        session.login()
        client = Client(session=session)
        semester = client.semester

        schedule = print_schedule(client, semester)
        out_path = save_schedule(schedule, semester)
        print(f"JSON 已保存至: {out_path}")

    except LoginError as exc:
        print(f"\n[错误] 登录失败: {exc}")
        print("请确认:\n  1. TJU_USER / TJU_PASS 环境变量已正确设置\n  2. 已连接校园网或 VPN")
        sys.exit(1)
    except (DataError, HtmlParseError) as exc:
        print(f"\n[错误] 数据解析失败: {exc}")
        sys.exit(1)
