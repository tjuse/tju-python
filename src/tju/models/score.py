"""Models for academic scores (undergraduate, graduate, and experiment)."""

from typing import Annotated, Optional

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass

from tju.fields import ChineseBool, ExpScoreSemesterField, GPAField, ScoreSemesterField
from tju.schema import LoadDumpSchema, mfield

from .base import Result, Results


@dataclass(frozen=True, base_schema=LoadDumpSchema)
class ScoreSummary(Result):
    """Aggregate score statistics (shared base for UG and GS summaries)."""

    courses_count: Optional[int] = mfield(default=None, data_key="门数")
    total_credit: Optional[float] = mfield(default=None, data_key="总学分")


@dataclass(frozen=True, base_schema=LoadDumpSchema)
class UGScoreSummary(ScoreSummary):
    """Undergraduate score summary, includes GPA and weighted average."""

    gpa: Optional[float] = mfield(default=None, data_key="平均绩点")
    score: Optional[float] = mfield(default=None, data_key="加权平均成绩")


@dataclass(frozen=True, base_schema=LoadDumpSchema)
class GSScoreSummary(ScoreSummary):
    """Graduate score summary, broken down by school year and term."""

    school_year: Optional[str] = mfield(default=None, data_key="学年度")
    term: Optional[int] = mfield(default=None, data_key="学期")


# fmt: off
@dataclass(frozen=True, base_schema=LoadDumpSchema)
class Score(Result):
    """Base score record shared by :class:`UGScore` and :class:`GSScore`."""

    semester: Annotated[Optional[str], ScoreSemesterField] = mfield(default=None, data_key="学年学期")
    course_id: Optional[str] = mfield(default=None, data_key="课程代码")
    name: Optional[str] = mfield(default=None, data_key="课程名称")
    course_type: Optional[str] = mfield(default=None, data_key="课程类别")
    credit: Optional[float] = mfield(default=None, data_key="学分")


@dataclass(frozen=True, base_schema=LoadDumpSchema)
class UGScore(Score):
    """An undergraduate course score record."""

    course_props: Optional[str] = mfield(default=None, data_key="课程性质")
    score: Optional[str] = mfield(default=None, data_key="总评成绩")
    gpa: Annotated[Optional[float], GPAField] = mfield(default=None, data_key="绩点")

    class Meta:
        unknown = EXCLUDE

@dataclass(frozen=True, base_schema=LoadDumpSchema)
class GSScore(Score):
    """A graduate course score record."""

    class_id: Optional[str] = mfield(default=None, data_key="课程序号")
    exam_status: Optional[str] = mfield(default=None, data_key="考试情况")
    score: Optional[str] = mfield(default=None, data_key="最终")
    is_in_plan: Annotated[Optional[str], ChineseBool] = mfield(default=None, data_key="是否方案内课程")
    is_credited: Annotated[Optional[str], ChineseBool] = mfield(default=None, data_key="选修课是否认定学分")

    class Meta:
        unknown = EXCLUDE


@dataclass(frozen=True, base_schema=LoadDumpSchema)
class ExpScore(Result):
    """An experiment (lab) course score record."""

    semester: Annotated[Optional[str], ExpScoreSemesterField] = mfield(default=None, data_key="学年学期")
    course_id: Optional[str] = mfield(default=None, data_key="课程代码")
    class_id: Optional[str] = mfield(default=None, data_key="课程序号")
    course_name: Optional[str] = mfield(default=None, data_key="课程名称")
    project_id: Optional[str] = mfield(default=None, data_key="项目代码")
    project_name: Optional[str] = mfield(default=None, data_key="项目名称")
    sub_score: Optional[str] = mfield(default=None, data_key="分项成绩")
    score: Optional[float] = mfield(default=None, data_key="项目成绩")

    class Meta:
        unknown = EXCLUDE


class UGScores(Results[UGScore]):
    """List of undergraduate course scores."""

    _item = UGScore


class GSScores(Results[GSScore]):
    """List of graduate course scores."""

    _item = GSScore


class ExpScores(Results[ExpScore]):
    """List of experiment/lab course scores."""

    _item = ExpScore


class UGScoreSummarys(Results[UGScoreSummary]):
    """List of undergraduate score summaries."""

    _item = UGScoreSummary


class GSScoreSummarys(Results[GSScoreSummary]):
    """List of graduate score summaries."""

    _item = GSScoreSummary
