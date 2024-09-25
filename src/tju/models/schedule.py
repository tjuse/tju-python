from typing import Optional

from marshmallow_dataclass import dataclass

from tju.schema import mfield

from .base import Result, Results


@dataclass(frozen=True)
class CourseArrange(Result):
    teacher: Optional[list] = mfield(default=None)
    week: Optional[list] = mfield(default=None)
    unit: Optional[list] = mfield(default=None)
    weekday: Optional[int] = mfield(default=None)
    location: Optional[str] = mfield(default=None)


@dataclass(frozen=True)
class Course(Result):
    class_id: Optional[str] = mfield(default=None)
    course_id: Optional[str] = mfield(default=None)
    name: Optional[str] = mfield(default=None)
    credit: Optional[float] = mfield(default=None)
    campus: Optional[str] = mfield(default=None)
    weeks: Optional[str] = mfield(default=None)
    arrange: Optional[list[CourseArrange]] = mfield(default=None)
    teacher: Optional[list] = mfield(default=None)


class Schedule(Results[Course]):
    _item = Course
