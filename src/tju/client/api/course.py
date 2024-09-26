from __future__ import annotations

from tju.consts import COURSELIB_URL_PATH, SEMESTER
from tju.exceptions import DataError, HtmlParseError, StuTypeError
from tju.models import CourseLib, StuType
from tju.parser import parse_course

from ..base import BaseClient


class CourseMixin(BaseClient):
    def __init__(self):
        super().__init__()

    def query_courses(
        self,
        stu_type: StuType | int | None = None,
        semester: str | None = None,
        page_no: int | None = None,
        page_size: int | None = None,
        **kwargs,
    ):
        """
        public course lib
        """
        if stu_type is None:
            stu_type = self.stu_type
        if stu_type == StuType.UNDERGRADUATE or stu_type == 1:
            project_id = 1
        elif stu_type == StuType.GRADUATE or stu_type == 2:
            project_id = 22
        else:
            raise StuTypeError(f"Invalid student type: {stu_type}")

        if semester is None:
            semester = self.semester
        if semester not in SEMESTER:
            raise DataError(f"Semester {semester} not found")
        semester_id = SEMESTER[semester]

        if page_no is None:
            page_no = 1

        if page_size is None:
            page_size = 10
        elif page_size > 1000:
            page_size = 1000

        course_html = self._session.get(
            COURSELIB_URL_PATH,
            params={
                "lesson.project.id": project_id,
                "lesson.semester.id": semester_id,
                "pageNo": str(page_no),
                "pageSize": str(page_size),
            },
            **kwargs,
        ).text

        try:
            course_dict = parse_course(course_html)
        except IndexError:
            raise HtmlParseError from None
        course = CourseLib()
        if "list" in course_dict:
            course.load(data=course_dict["list"])
            course_dict["list"] = course
        return course_dict
