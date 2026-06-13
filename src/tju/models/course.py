"""Models for the public course library (``query_courses``)."""

from typing import Annotated, Optional

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass

from tju.fields import ChineseBool, ChineseHasBool
from tju.schema import LoadDumpSchema, mfield

from .base import Results
from .schedule import Course, CourseArrange


# fmt: off
@dataclass(frozen=True, base_schema=LoadDumpSchema)
class LibCourse(Course):
    """A course entry from the public course library.  Extends :class:`~tju.models.schedule.Course`
    with library-specific fields such as ``lession_id``, ``course_type``, enrollment limits,
    and ``has_syllabus``.  The ``selected``/``limit`` fields are populated for UG courses
    (16-column format) but are ``None`` for GS courses (12-column format)."""
    # key in Course
    class_id: Optional[str] = mfield(default=None, data_key="课程序号")
    course_id: Optional[str] = mfield(default=None, data_key="课程代码")
    name: Optional[str] = mfield(default=None, data_key="课程名称")
    credit: Optional[float] = mfield(default=None, data_key="学分")
    campus: Optional[str] = mfield(default=None, data_key="开课校区")
    weeks: Optional[str] = mfield(default=None, data_key="起止周")
    arrange: Optional[list[CourseArrange]] = mfield(default=None)
    teacher: Optional[list] = mfield(default=None, data_key="教师")
    # key in LibCourse
    semester: Optional[str] = mfield(default=None)
    lession_id: Optional[str] = mfield(default=None)
    course_type: Optional[list] = mfield(default=None, data_key="课程类别")
    teaching_class: Optional[list] = mfield(default=None, data_key="教学班")
    selected: Optional[int] = mfield(default=None, data_key="实际")
    limit: Optional[int] = mfield(default=None, data_key="总上限")
    extra_limit: Optional[int] = mfield(default=None, data_key="计划外人数上限")
    is_extra_open: Annotated[Optional[bool], ChineseBool] = mfield(default=None, data_key="是否开放计划外")
    hours: Optional[float] = mfield(default=None, data_key="总学时")
    week_hours: Optional[float] = mfield(default=None, data_key="周学时")
    has_syllabus: Annotated[Optional[bool], ChineseHasBool] = mfield(default=None, data_key="课程大纲")

    class Meta:
        unknown = EXCLUDE


class CourseLib(Results[LibCourse]):
    """List of :class:`LibCourse` items from the public course library."""

    _item = LibCourse
