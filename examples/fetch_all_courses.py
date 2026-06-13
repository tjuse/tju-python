"""Fetch and save the full public course library for the current semester.

Crawls both the undergraduate (project 1) and graduate (project 22) course
libraries, merges them, and writes the complete list to
examples/output/courses_<semester>.json.

Each record in the output JSON has an extra ``student_type`` field:
  "undergraduate"  — course_id typically starts with a digit
  "graduate"       — course_id typically starts with S or B

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
from tju.models.common import StuType
from tju.models.course import LibCourse

PAGE_SIZE = 1000          # maximum accepted by the EAMS API
PAGE_DELAY = 0.8          # seconds between page requests (avoid rate-limiting)
PROJECT_DELAY = 1.5       # extra pause between the two project fetches
SAMPLE_SIZE = 10          # courses shown in the console preview


def fetch_project(
    client: Client, semester: str, stu_type: StuType, label: str
) -> list[LibCourse]:
    """Fetch all pages for one project (UG or GS) and return a flat list."""
    collected: list[LibCourse] = []

    first = client.query_courses(semester=semester, stu_type=stu_type,
                                 page_no=1, page_size=PAGE_SIZE)
    total: int = first["total"]
    collected.extend(first["list"])
    print(f"  [{label}] 第 1 页  ({len(collected)}/{total})")

    page_no = 2
    while len(collected) < total:
        time.sleep(PAGE_DELAY)
        page = client.query_courses(semester=semester, stu_type=stu_type,
                                    page_no=page_no, page_size=PAGE_SIZE)
        batch = page["list"]
        if not batch:
            break
        collected.extend(batch)
        print(f"  [{label}] 第 {page_no} 页  ({len(collected)}/{total})")
        page_no += 1

    return collected


def print_summary(
    client: Client, semester: str,
    ug_courses: list[LibCourse], gs_courses: list[LibCourse],
) -> None:
    all_courses = ug_courses + gs_courses
    print(f"\n{'=' * 60}")
    print(f"  学生: {client.stu_name}  ({client.stu_id})")
    print(f"  类型: {client.stu_type.name}")
    print(f"  学期: {semester}")
    print(f"  本科课程: {len(ug_courses)} 门")
    print(f"  研究生课程: {len(gs_courses)} 门")
    print(f"  合计: {len(all_courses)} 门")
    print(f"{'=' * 60}")

    print(f"\n前 {min(SAMPLE_SIZE, len(all_courses))} 门课程预览:\n")
    for i, course in enumerate(all_courses[:SAMPLE_SIZE], 1):
        credit_str = f"{course.credit:.1f}" if course.credit is not None else "?"
        teachers = "、".join(course.teacher) if course.teacher else "?"
        print(
            f"  [{i:2d}] {course.name or '?'}  "
            f"({credit_str} 学分)  {course.course_id or '?'}  "
            f"{course.campus or '?'}  [{teachers}]"
        )

    if len(all_courses) > SAMPLE_SIZE:
        print(f"\n  … 共 {len(all_courses)} 门，完整列表见 JSON 文件。")


def save_courses(
    ug_courses: list[LibCourse], gs_courses: list[LibCourse], semester: str
) -> Path:
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"courses_{semester}.json"

    ug_data = LibCourse.Schema(many=True).dump(ug_courses)
    for d in ug_data:
        d["student_type"] = "undergraduate"

    gs_data = LibCourse.Schema(many=True).dump(gs_courses)
    for d in gs_data:
        d["student_type"] = "graduate"

    out_path.write_text(
        json.dumps(ug_data + gs_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_path


if __name__ == "__main__":
    try:
        session = Session()
        session.login()
        client = Client(session=session)
        semester = client.semester

        print(f"\n正在爬取学期 {semester} 的本研全校课程 (每页 {PAGE_SIZE} 条):\n")

        # --- undergraduate (project_id=1) ---
        ug_courses: list[LibCourse] = []
        try:
            ug_courses = fetch_project(client, semester, StuType.UNDERGRADUATE, "本科")
        except (DataError, HtmlParseError) as exc:
            print(f"  [警告] 本科课程库获取失败: {exc}")
            print("  (该账号可能无权访问本科课程库，仅保存研究生课程)")

        time.sleep(PROJECT_DELAY)

        # --- graduate (project_id=22) ---
        gs_courses: list[LibCourse] = []
        try:
            gs_courses = fetch_project(client, semester, StuType.GRADUATE, "研究生")
        except (DataError, HtmlParseError) as exc:
            print(f"  [警告] 研究生课程库获取失败: {exc}")

        if not ug_courses and not gs_courses:
            print("\n[错误] 两个课程库均获取失败，退出。")
            sys.exit(1)

        print_summary(client, semester, ug_courses, gs_courses)

        out_path = save_courses(ug_courses, gs_courses, semester)
        print(f"\nJSON 已保存至: {out_path}")

    except LoginError as exc:
        print(f"\n[错误] 登录失败: {exc}")
        print("请确认:\n  1. TJU_USER / TJU_PASS 环境变量已正确设置\n  2. 已连接校园网或 VPN")
        sys.exit(1)
