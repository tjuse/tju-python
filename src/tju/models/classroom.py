from __future__ import annotations

from typing import Optional

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass

from tju.schema import LoadDumpSchema, mfield

from .base import Result, Results


# fmt: off
@dataclass(frozen=True, base_schema=LoadDumpSchema)
class FreeClassroom(Result):
    """A single free-classroom entry returned by the EAMS free-classroom search."""
    campus:     Optional[str] = mfield(default=None, data_key="校区")
    building:   Optional[str] = mfield(default=None, data_key="教学楼")
    name:       Optional[str] = mfield(default=None, data_key="教室")
    room_type:  Optional[str] = mfield(default=None, data_key="教室类型")
    seats:      Optional[str] = mfield(default=None, data_key="座位数")

    class Meta:
        unknown = EXCLUDE


class FreeClassrooms(Results[FreeClassroom]):
    _item = FreeClassroom
