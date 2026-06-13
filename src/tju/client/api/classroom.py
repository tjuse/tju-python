from __future__ import annotations

from tju.consts import (
    COURSETABLE_INDEX_URL_PATH,
    FREE_SEARCH_URL_PATH,
    FREE_SELECTION_URL_PATH,
)
from tju.exceptions import DataError, HtmlParseError
from tju.models.classroom import FreeClassrooms
from tju.models.common import StuType
from tju.parser.classroom import parse_free_classroom

from ..base import BaseClient


class ClassroomMixin(BaseClient):
    """Free classroom search (空闲教室查询)."""

    def __init__(self): ...

    def free_classrooms(
        self,
        date_begin: str,
        date_end: str | None = None,
        time_begin: str = "1",
        time_end: str = "12",
        by_unit: bool = True,
        campus_id: str | None = None,
        building_id: str | None = None,
        room_type_id: str | None = None,
        seats: int | None = None,
        name: str | None = None,
        cycle_type: int = 1,
        cycle_count: int = 1,
        **kwargs,
    ) -> FreeClassrooms:
        """
        Search for free classrooms on a given date/time range.

        Args:
            date_begin:    Start date in ``YYYY-MM-DD`` format (required).
            date_end:      End date; defaults to ``date_begin`` (single-day search).
            time_begin:    Start of the requested slot. Integer class-unit (1–12) when
                           ``by_unit=True`` (default); ``HH:MM`` clock time when ``False``.
            time_end:      End of the requested slot (same format as ``time_begin``).
            by_unit:       ``True`` — search by class-unit numbers (小节, default);
                           ``False`` — search by clock time (``HH:MM``).
            campus_id:     Campus filter: ``"2"`` 卫津路 / ``"3"`` 北洋园 / ``"4"`` all.
            building_id:   Building filter (optional; depends on campus).
            room_type_id:  Room type: ``"2"`` 普通教室 / ``"7"`` 多媒体 / etc.
            seats:         Minimum seat count filter (optional).
            name:          Classroom name substring filter (optional).
            cycle_type:    Recurrence unit: ``1`` daily (default), ``2`` weekly.
            cycle_count:   Number of recurrence cycles (default ``1``).
        """
        if date_end is None:
            date_end = date_begin

        project_id = 22 if self.stu_type == StuType.GRADUATE else 1

        # The classroom search module requires an active project context in the session.
        self._session.get(
            COURSETABLE_INDEX_URL_PATH,
            params={"projectId": project_id},
            **kwargs,
        )
        self._session.get(FREE_SELECTION_URL_PATH, **kwargs)

        search_html = self._session.post(
            FREE_SEARCH_URL_PATH,
            data={
                "seats": str(seats) if seats is not None else "",
                "classroom.name": name or "",
                "classroom.type.id": str(room_type_id) if room_type_id is not None else "",
                "classroom.campus.id": str(campus_id) if campus_id is not None else "",
                "classroom.building.id": str(building_id) if building_id is not None else "",
                "cycleTime.cycleType": str(cycle_type),
                "cycleTime.cycleCount": str(cycle_count),
                "cycleTime.dateBegin": date_begin,
                "cycleTime.dateEnd": date_end,
                "roomApplyTimeType": "0" if by_unit else "1",
                "timeBegin": str(time_begin),
                "timeEnd": str(time_end),
            },
            **kwargs,
        ).text

        try:
            classroom_list = parse_free_classroom(search_html)
        except IndexError:
            raise HtmlParseError from None

        classrooms = FreeClassrooms()
        classrooms.load(data=classroom_list)
        return classrooms
