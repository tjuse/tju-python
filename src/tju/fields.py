"""Custom marshmallow :class:`~marshmallow.fields.Field` subclasses for
deserialising Chinese-format values from EAMS HTML data.

Includes gender/student-type converters, date formatters, Chinese boolean
fields (是/有), exam-time range splitter, and GPA/semester normalisation.
"""

from __future__ import annotations

import re
from datetime import date, datetime

from marshmallow.fields import Field

from tju.models import Gender
from tju.models.common import StuType


class ChineseGender(Field):
    def _serialize(self, value: Gender, attr: str, obj: object, **kwargs) -> str:
        return value.value

    def _deserialize(
        self, value: str, attr: str, data: dict, **kwargs
    ) -> Gender | None:
        return (
            Gender.MALE
            if value == Gender.MALE.value
            else Gender.FEMALE
            if value == Gender.FEMALE.value
            else None
        )


class ChineseStuType(Field):
    def _serialize(self, value: StuType, attr: str, obj: object, **kwargs) -> str:
        return value.value

    def _deserialize(
        self, value: str, attr: str, data: dict, **kwargs
    ) -> StuType | None:
        return (
            StuType.UNDERGRADUATE
            if value == StuType.UNDERGRADUATE.value
            else StuType.GRADUATE
            if value == StuType.GRADUATE.value
            else None
        )


class DatetimeField(Field):
    def __init__(self, template: str | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.template = template if template is not None else "%Y-%m-%d"

    def _serialize(self, value: date, attr: str, obj: object, **kwargs) -> str:
        return value.strftime(self.template)

    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> date | None:
        return datetime.strptime(value, self.template).date() if value else None


class ChineseBool(Field):
    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> bool | None:
        return value == "是" if value else None


class ChineseHasBool(Field):
    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> bool | None:
        return value == "有" if value else None


class ExamTimeField(Field):
    """09:00~11:00"""

    def _serialize(self, value: list, attr: str, obj: object, **kwargs) -> list:
        return [_.strftime("%H:%M") for _ in value]

    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> list | None:
        if value is None:
            return None
        return [datetime.strptime(_, "%H:%M").time() for _ in value.split("~")]


class ScoreSemesterField(Field):
    d_pattern = re.compile(r"20(\d{2})-20(\d{2}) (\d)")
    s_pattern = re.compile(r"(\d{2})(\d{2})(\d)")

    def _serialize(self, value: str, attr: str, obj: object, **kwargs) -> str:
        if self.s_pattern.findall(value):
            return re.sub(self.s_pattern, r"20\1-20\2 \3", value)
        return value

    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> str | None:
        if self.d_pattern.findall(value):
            return re.sub(self.d_pattern, r"\1\2\3", value)
        return value


class GPAField(Field):
    def _serialize(self, value: float | None, attr: str, obj: object, **kwargs) -> str:
        return str(value) if value else ""

    def _deserialize(
        self, value: float, attr: str, data: dict, **kwargs
    ) -> float | None:
        return float(value) if value else None


class ExpScoreSemesterField(Field):
    d_pattern = re.compile(r"20(\d{2})-20(\d{2})学年(\d)学期")
    s_pattern = re.compile(r"(\d{2})(\d{2})(\d)")

    def _serialize(self, value: str, attr: str, obj: object, **kwargs) -> str:
        if self.s_pattern.findall(value):
            return re.sub(self.s_pattern, r"20\1-20\2学年\3学期", value)
        return value

    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> str | None:
        if self.d_pattern.findall(value):
            return re.sub(self.d_pattern, r"\1\2\3", value)
        return value
