"""Models for the exam schedule."""

from datetime import date
from typing import Annotated, Optional

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass

from tju.fields import DatetimeField, ExamTimeField
from tju.schema import LoadDumpSchema, mfield

from .base import Result, Results


# fmt: off
@dataclass(frozen=True, base_schema=LoadDumpSchema)
class Exam(Result):
    """A single exam entry.  ``exam_time`` is a list of two ``datetime.time`` objects
    (start, end); ``exam_date`` is a ``datetime.date``."""

    class_id: Optional[str] = mfield(default=None, data_key="课程序号")
    name: Optional[str] = mfield(default=None, data_key="课程名称")
    exam_type: Optional[str] = mfield(default=None, data_key="考试类别")
    exam_date: Annotated[Optional[date], DatetimeField] = mfield(default=None, data_key="考试日期")
    exam_category: Optional[str] = mfield(default=None, data_key="批次")
    exam_time: Annotated[Optional[list], ExamTimeField] = mfield(default=None, data_key="考试安排")
    location: Optional[str] = mfield(default=None, data_key="考试地点")
    seat: Optional[str] = mfield(default=None, data_key="考场座位号")
    status: Optional[str] = mfield(default=None, data_key="考试情况")
    notice: Optional[str] = mfield(default=None, data_key="其它说明")

    class Meta:
        unknown = EXCLUDE


class Exams(Results[Exam]):
    """List of :class:`Exam` items from the exam schedule page."""

    _item = Exam
