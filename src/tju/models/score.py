from typing import Annotated, Optional

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass

from tju.fields import ChineseBool, GPAField, ScoreSemesterField
from tju.schema import LoadDumpSchema, mfield

from .base import Result, Results


@dataclass(frozen=True, base_schema=LoadDumpSchema)
class ScoreSummary(Result):
    # common
    courses_count: Optional[int] = mfield(default=None, data_key="门数")
    total_credit: Optional[float] = mfield(default=None, data_key="总学分")
    # undergraduate
    gpa: Optional[float] = mfield(default=None, data_key="平均绩点")
    score: Optional[float] = mfield(default=None, data_key="加权平均成绩")
    # graduate
    school_year: Optional[str] = mfield(default=None, data_key="学年度")
    term: Optional[int] = mfield(default=None, data_key="学期")


# fmt: off
@dataclass(frozen=True, base_schema=LoadDumpSchema)
class Score(Result):
    # common
    semester: Annotated[Optional[str], ScoreSemesterField] = mfield(default=None, data_key="学年学期")
    course_id: Optional[str] = mfield(default=None, data_key="课程代码")
    name: Optional[str] = mfield(default=None, data_key="课程名称")
    course_type: Optional[str] = mfield(default=None, data_key="课程类别")
    credit: Optional[float] = mfield(default=None, data_key="学分")

    # undergraduate
    course_props: Optional[str] = mfield(default=None, data_key="课程性质")
    score: Optional[str] = mfield(default=None, data_key="总评成绩")
    gpa: Annotated[Optional[float], GPAField] = mfield(default=None, data_key="绩点")

    # TODO: exclude this when undergraduate
    # graduate
    class_id: Optional[str] = mfield(default=None, data_key="课程序号")
    exam_status: Optional[str] = mfield(default=None, data_key="考试情况")
    score: Optional[str] = mfield(default=None, data_key="最终")
    is_in_plan: Annotated[Optional[str], ChineseBool] = mfield(default=None, data_key="是否方案内课程")
    is_credited: Annotated[Optional[str], ChineseBool] = mfield(default=None, data_key="选修课是否认定学分")

    class Meta:
        unknown = EXCLUDE


class Scores(Results[Score]):
    _item = Score


class ScoreSummarys(Results[ScoreSummary]):
    _item = ScoreSummary
