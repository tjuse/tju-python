"""Helpers for converting tju model objects into Textual display widgets.

All rendering is done from serialised dicts (via ``Model.Schema().dump()``)
so this module has no direct dependency on the model classes themselves —
only on Textual and stdlib.
"""

from __future__ import annotations

from typing import Any

from textual.widgets import DataTable, Markdown

from .widgets import VimDataTable

# ---------------------------------------------------------------------------
# Profile — full ordered label map (covers UG + GS; only non-empty shown)
# ---------------------------------------------------------------------------

_PROFILE_LABELS: list[tuple[str, str]] = [
    ("stu_id", "学号"),
    ("stu_name", "姓名"),
    ("stu_name_en", "英文名"),
    ("gender", "性别"),
    ("stu_type", "学生类别"),
    ("edu_level", "学历层次"),
    ("grade", "年级"),
    ("edu_system", "学制"),
    ("project", "项目"),
    ("faculty", "院系"),
    ("major", "专业"),
    ("direction", "方向"),
    ("admin_faculty", "行政管理院系"),
    ("admin_class", "行政班"),
    ("campus", "校区"),
    ("study_form", "学习形式"),
    ("supervisor", "导师"),
    ("co_supervisor", "合作导师"),
    ("scholarship_supervisor", "助学金导师"),
    ("degree_category", "学位类别"),
    ("training_plan", "培养方案"),
    ("training_type", "培养类型"),
    ("training_mode", "培养模式"),
    ("enrollment_date", "入学日期"),
    ("graduation_date", "预毕业时间"),
    ("effective_date", "学籍生效日期"),
    ("stu_status", "学籍状态"),
    ("is_enrolled", "是否在籍"),
    ("is_on_campus", "是否在校"),
    ("has_enrolled", "是否有学籍"),
    ("total_tuition", "总学费"),
    ("cooperative_unit", "合作单位"),
    ("orientation_unit", "定向单位"),
    ("email", "电子邮件"),
    ("phone", "联系电话"),
    ("mobile", "移动电话"),
    ("address", "联系地址"),
    ("home_phone", "家庭电话"),
    ("home_address", "家庭地址"),
    ("remark", "备注"),
]

# ---------------------------------------------------------------------------
# Column subsets for each feature (order matters)
# ---------------------------------------------------------------------------

_SCHEDULE_COLS = ["name", "class_id", "credit", "campus", "weeks", "teacher"]
_SCHEDULE_LABELS = {
    "name": "课程名称", "class_id": "课程序号", "credit": "学分",
    "campus": "校区", "weeks": "周次", "teacher": "教师",
}

_EXAM_COLS = ["name", "class_id", "exam_type", "exam_date", "exam_time",
              "location", "seat", "status"]
_EXAM_LABELS = {
    "name": "课程名称", "class_id": "课程序号", "exam_type": "考试类别",
    "exam_date": "考试日期", "exam_time": "考试时间",
    "location": "考试地点", "seat": "座位号", "status": "考试情况",
}

_COURSE_COLS = ["class_id", "name", "credit", "campus", "weeks", "teacher",
                "course_type", "selected", "limit", "hours"]
_COURSE_LABELS = {
    "class_id": "课程序号", "name": "课程名称", "credit": "学分",
    "campus": "校区", "weeks": "周次", "teacher": "教师",
    "course_type": "课程类别", "selected": "已选", "limit": "上限",
    "hours": "总学时",
}

_UGSCORE_COLS = ["semester", "course_id", "name", "course_type",
                 "course_props", "credit", "score", "gpa"]
_UGSCORE_LABELS = {
    "semester": "学期", "course_id": "课程代码", "name": "课程名称",
    "course_type": "课程类别", "course_props": "课程性质",
    "credit": "学分", "score": "成绩", "gpa": "绩点",
}

_GSSCORE_COLS = ["semester", "course_id", "class_id", "name",
                 "course_type", "credit", "score", "exam_status"]
_GSSCORE_LABELS = {
    "semester": "学期", "course_id": "课程代码", "class_id": "课程序号",
    "name": "课程名称", "course_type": "课程类别",
    "credit": "学分", "score": "成绩", "exam_status": "考试情况",
}

_EXPSCORE_COLS = ["semester", "course_id", "course_name",
                  "project_name", "sub_score", "score"]
_EXPSCORE_LABELS = {
    "semester": "学期", "course_id": "课程代码",
    "course_name": "课程名称", "project_name": "项目名称",
    "sub_score": "分项成绩", "score": "项目成绩",
}

_CLASSROOM_COLS = ["campus", "building", "name", "room_type", "seats"]
_CLASSROOM_LABELS = {
    "campus": "校区", "building": "教学楼",
    "name": "教室", "room_type": "教室类型", "seats": "座位数",
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------


def _fmt(value: Any) -> str:
    """Format a cell value for display."""
    if value is None:
        return ""
    if isinstance(value, list):
        return "、".join(_fmt(v) for v in value)
    if isinstance(value, bool):
        return "是" if value else "否"
    return str(value)


def _build_table(
    rows: list[dict[str, Any]],
    cols: list[str],
    labels: dict[str, str],
) -> DataTable:
    """Return a populated :class:`~textual.widgets.DataTable` from *rows*."""
    table: DataTable = VimDataTable(zebra_stripes=True, cursor_type="row")
    for col in cols:
        table.add_column(labels.get(col, col), key=col)
    for row in rows:
        table.add_row(*[_fmt(row.get(c)) for c in cols])
    return table


# ---------------------------------------------------------------------------
# Public render functions — each accepts the raw .dump() output
# ---------------------------------------------------------------------------


def render_profile(data: dict[str, Any]) -> DataTable:
    """Two-column key/value table showing every non-empty profile field."""
    table: DataTable = VimDataTable(zebra_stripes=True, cursor_type="row")
    table.add_column("字段", key="key")
    table.add_column("值", key="value")
    for field, label in _PROFILE_LABELS:
        v = data.get(field)
        if v not in (None, "", []):
            table.add_row(label, _fmt(v))
    return table


def render_schedule(rows: list[dict[str, Any]]) -> DataTable:
    """Table for serialised Course list from personal timetable."""
    return _build_table(rows, _SCHEDULE_COLS, _SCHEDULE_LABELS)


def render_exam(rows: list[dict[str, Any]]) -> DataTable:
    """Table for serialised Exam list."""
    return _build_table(rows, _EXAM_COLS, _EXAM_LABELS)


def render_courses(rows: list[dict[str, Any]]) -> DataTable:
    """Table for serialised LibCourse list from the public course library."""
    return _build_table(rows, _COURSE_COLS, _COURSE_LABELS)


def render_ug_scores(rows: list[dict[str, Any]]) -> DataTable:
    """Table for serialised UGScore list."""
    return _build_table(rows, _UGSCORE_COLS, _UGSCORE_LABELS)


def render_gs_scores(rows: list[dict[str, Any]]) -> DataTable:
    """Table for serialised GSScore list."""
    return _build_table(rows, _GSSCORE_COLS, _GSSCORE_LABELS)


def render_exp_scores(rows: list[dict[str, Any]]) -> DataTable:
    """Table for serialised ExpScore list."""
    return _build_table(rows, _EXPSCORE_COLS, _EXPSCORE_LABELS)


def render_classrooms(rows: list[dict[str, Any]]) -> DataTable:
    """Table for serialised FreeClassroom list."""
    return _build_table(rows, _CLASSROOM_COLS, _CLASSROOM_LABELS)


def render_markdown(text: str) -> Markdown:
    """Wrap a Markdown string in a Textual Markdown widget."""
    return Markdown(text)
