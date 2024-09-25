"""
schedule
"""

from __future__ import annotations

import re
import time

from tju.client.base import BaseClient
from tju.consts import (
    COURSETABLE_GET_URL_PATH,
    COURSETABLE_INDEX_URL_PATH,
    COURSETABLE_URL_PATH,
    SEMESTER,
)
from tju.exceptions import CourseError, HtmlParseError, SemesterError
from tju.models.base import Results
from tju.models.common import StuType
from tju.models.schedule import Course, Schedule
from tju.parser import parse_schedule


class ScheduleMixin(BaseClient):
    """
    personal schedule
    """

    def __init__(self):
        super().__init__()

    def schedule(
        self,
        semester: str | None = None,
        query_minor: bool = False,
        query_class: bool = False,
        **kwargs,
    ) -> Results[Course]:
        """
        self course table
        """
        is_gs = self.stu_type == StuType.GRADUATE
        has_minor = self.has_minor

        if not has_minor and query_minor:
            raise CourseError("No minor classes")

        if semester is None:
            semester = self.semester
        if semester not in SEMESTER:
            raise SemesterError(f"Semester {semester} not found")
        semester_id = SEMESTER[semester]

        if is_gs:
            project_id = 22  # graduate
        elif has_minor and query_minor:
            project_id = 2  # minor
        else:
            project_id = 1  # major

        if not is_gs:
            self._session.get(
                COURSETABLE_INDEX_URL_PATH, params={"projectId": project_id}, **kwargs
            )
            time.sleep(0.1)

        index_html = self._session.get(
            COURSETABLE_GET_URL_PATH, params={"projectId": project_id}, **kwargs
        ).text
        ids_list = re.findall('"ids","([^"]+)"', index_html)
        if len(ids_list) == 0:
            raise HtmlParseError("Cannot find ids")
        ids = ids_list[0]
        time.sleep(0.1)

        schedule_html = self._session.post(
            COURSETABLE_URL_PATH,
            params={
                "ignoreHead": "1",
                "setting.kind": "std" if not query_class else "class",
                "startWeek": "",
                "semester.id": semester_id,
                "ids": ids,
            },
            **kwargs,
        ).text

        try:
            schedule_dict = parse_schedule(schedule_html)
        except IndexError as exc:
            raise HtmlParseError from exc

        schedule = Schedule()
        schedule.load(data=schedule_dict)

        return schedule
