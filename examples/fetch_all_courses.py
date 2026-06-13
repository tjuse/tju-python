"""Fetch and save the full public course library for the current semester.

Crawls every page of the EAMS course library (up to 1000 courses per request)
and writes the complete list to examples/output/courses_<semester>.json.

Run:
    uv run --env-file .env python examples/fetch_all_courses.py

Requires TJU_USER and TJU_PASS to be set (env vars or .env file) and an
active campus network connection or VPN.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

# Allow running the script from the repo root without an editable install.
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from tju import Session
from tju.client import Client
from tju.exceptions import DataError, HtmlParseError, LoginError
from tju.models.course import LibCourse

PAGE_SIZE = 1000          # maximum accepted by the EAMS API
PAGE_DELAY = 0.8          # seconds between page requests (avoid rate-limiting)
SAMPLE_SIZE = 10          # number of courses shown in the console summary


def fetch_all(client: Client, semester: str) -> list[LibCourse]:
    """Return every LibCourse in the public course library for *semester*."""
    collected: list[LibCourse] = []

    first = client.query_courses(semester=semester, page_no=1, page_size=PAGE_SIZE)
    total: int = first["total"]
    collected.extend(first["list"])
    print(f"  第 1 页  ({len(collected)}/{total})")

    page_no = 2
    while len(collected) < total:
        time.sleep(PAGE_DELAY)
        page = client.query_courses(semester=semester, page_no=page_no, page_size=PAGE_SIZE)
        batch = page["list"]
        if not batch:          # defensive: stop if server returns empty page early
            break
        collected.extend(batch)
        print(f"  第 {page_no} 页  ({len(collected)}/{total})")
        page_no += 1

    return collected


def print_summary(client: Client, semester: str, courses: list[LibCourse]) -> None:
    print(f"\n{'=' * 60}")
    print(f"  学生: {client.stu_name}  ({client.stu_id})")
    print(f"  类型: {client.stu_type.name}")
    print(f"  学期: {semester}")
    print(f"  课程总数: {len(courses)}")
    print(f"{'=' * 60}")

    print(f"\n前 {min(SAMPLE_SIZE, len(courses))} 门课程预览:\n")
    for i, course in enumerate(courses[:SAMPLE_SIZE], 1):
        credit_str = f"{course.credit:.1f}" if course.credit is not None else "?"
        teachers = "、".join(course.teacher) if course.teacher else "?"
        print(
            f"  [{i:2d}] {course.name or '?'}  "
            f"({credit_str} 学分)  {course.course_id or '?'}  "
            f"{course.campus or '?'}  [{teachers}]"
        )

    if len(courses) > SAMPLE_SIZE:
        print(f"\n  … 共 {len(courses)} 门，完整列表见 JSON 文件。")


def save_courses(courses: list[LibCourse], semester: str) -> Path:
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"courses_{semester}.json"

    data = LibCourse.Schema(many=True).dump(courses)
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

        print(f"\n正在爬取学期 {semester} 的全部课程 (每页 {PAGE_SIZE} 条):\n")
        courses = fetch_all(client, semester)

        print_summary(client, semester, courses)

        out_path = save_courses(courses, semester)
        print(f"\nJSON 已保存至: {out_path}")

    except LoginError as exc:
        print(f"\n[错误] 登录失败: {exc}")
        print("请确认:\n  1. TJU_USER / TJU_PASS 环境变量已正确设置\n  2. 已连接校园网或 VPN")
        sys.exit(1)
    except (DataError, HtmlParseError) as exc:
        print(f"\n[错误] 数据解析失败: {exc}")
        sys.exit(1)
