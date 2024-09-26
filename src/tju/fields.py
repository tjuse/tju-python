from __future__ import annotations

from datetime import date, datetime

from marshmallow.fields import Field

from tju.models import Gender
from tju.models.common import StuType


class ChineseGender(Field):
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
    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> date | None:
        return datetime.strptime(value, "%Y-%m-%d").date() if value else None


class ChineseBool(Field):
    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> bool | None:
        return value == "是" if value else None


class ChineseHasBool(Field):
    def _deserialize(self, value: str, attr: str, data: dict, **kwargs) -> bool | None:
        return value == "有" if value else None
