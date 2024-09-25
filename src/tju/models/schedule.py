from dataclasses import field
from typing import Optional

from marshmallow_dataclass import dataclass

from tju.models.base import Result, Results


@dataclass(frozen=True)
class CourseArrange(Result):
    teacher: Optional[list] = field(default=None)
    week: Optional[list] = field(default=None)
    unit: Optional[list] = field(default=None)
    weekday: Optional[int] = field(default=None)
    location: Optional[str] = field(default=None)


@dataclass(frozen=True)
class ScheduleCourse(Result):
    class_id: Optional[str] = field(default=None)
    course_id: Optional[str] = field(default=None)
    name: Optional[str] = field(default=None)
    credit: Optional[float] = field(default=None)
    campus: Optional[str] = field(default=None)
    weeks: Optional[str] = field(default=None)
    arrange: Optional[list[CourseArrange]] = field(default=None)
    teacher: Optional[list] = field(default=None)


class Schedule(Results[ScheduleCourse]):
    _item = ScheduleCourse
