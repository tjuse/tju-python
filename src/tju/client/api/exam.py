from __future__ import annotations

from tju.consts import EXAM_POST_URL_PATH, EXAM_URL_PATH, SEMESTER
from tju.exceptions import DataError, HtmlParseError
from tju.models import Exams
from tju.parser import parse_exam, parse_exam_batch_id

from ..base import BaseClient


class ExamMixin(BaseClient):
    """
    exam
    """

    def __init__(self): ...

    def exam(
        self, semester: str | None = None, query_minor: bool = False, **kwargs
    ) -> list:
        """
        exam
        """
        has_minor = self.has_minor

        if not has_minor and query_minor:
            raise DataError("No minor exam")

        if semester is None:
            semester = self.semester
        if semester not in SEMESTER:
            raise DataError(f"Semester {semester} not found")
        semester_id = SEMESTER[semester]

        exam_post_html = self._session.post(
            EXAM_POST_URL_PATH,
            data={
                "semester.id": semester_id,
            },
            **kwargs,
        ).text

        try:
            exam_batch_id = parse_exam_batch_id(exam_post_html)
        except IndexError:
            raise HtmlParseError from None

        exam_html = self._session.get(
            EXAM_URL_PATH,
            params={
                "examBatch.id": exam_batch_id,
            },
        ).text

        with open("exam.html", "w", encoding="utf-8") as f:
            f.write(exam_html)

        try:
            exam_list = parse_exam(exam_html)
        except IndexError:
            raise HtmlParseError from None

        exams = Exams()
        exams.load(data=exam_list)

        return exams
