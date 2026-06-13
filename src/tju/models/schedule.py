"""Models for the personal timetable (schedule)."""

from typing import Optional

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass

from tju.schema import mfield

from .base import Result, Results


@dataclass(frozen=True)
class CourseArrange(Result):
    """A single scheduled slot (day / period / location) for a course."""

    teacher: Optional[list] = mfield(default=None)
    week: Optional[list] = mfield(default=None)
    unit: Optional[list] = mfield(default=None)
    weekday: Optional[int] = mfield(default=None)
    location: Optional[str] = mfield(default=None)


@dataclass(frozen=True)
class Course(Result):
    """A course entry on a personal timetable.  ``arrange`` holds the list of
    :class:`CourseArrange` slots; ``weeks`` is the raw week-range string."""

    class_id: Optional[str] = mfield(default=None)
    course_id: Optional[str] = mfield(default=None)
    name: Optional[str] = mfield(default=None)
    credit: Optional[float] = mfield(default=None)
    campus: Optional[str] = mfield(default=None)
    weeks: Optional[str] = mfield(default=None)
    arrange: Optional[list[CourseArrange]] = mfield(default=None)
    teacher: Optional[list] = mfield(default=None)

    class Meta:
        unknown = EXCLUDE


class Schedule(Results[Course]):
    """List of :class:`Course` items representing a personal timetable."""

    _item = Course
