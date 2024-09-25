from typing import Optional

from marshmallow_dataclass import dataclass

from tju.schema import mfield

from .schedule import Course, CourseArrange


@dataclass(frozen=True)
class LibCourse(Course):
    # TODO: bind keys
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
    course_type: Optional[list] = mfield(default=None, data_key="课程类别")
    teaching_class: Optional[list] = mfield(default=None, data_key="教学班")
    selected: Optional[int] = mfield(default=None, data_key="实际")
    limit: Optional[int] = mfield(default=None, data_key="总上限")
    extra_limit: Optional[int] = mfield(default=None, data_key="计划外人数上限")
    is_extra_open: Optional[bool] = mfield(default=None, data_key="是否开放计划外")
    hours: Optional[int] = mfield(default=None, data_key="总学时")
    week_hours: Optional[int] = mfield(default=None, data_key="周学时")
    has_syllabus: Optional[bool] = mfield(default=None, data_key="课程大纲")
