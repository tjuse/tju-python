from __future__ import annotations

from tju.consts import (
    COURSETABLE_INDEX_URL_PATH,
    SCORE_EXP_URL_PATH,
    SCORE_HISTORY_URL_PATH,
    SCORE_SEARCH_URL_PATH,
    SEMESTER,
)
from tju.exceptions import DataError, HtmlParseError
from tju.models import (
    ExpScores,
    GSScores,
    GSScoreSummarys,
    StuType,
    UGScores,
    UGScoreSummarys,
)
from tju.parser import parse_score, parse_score_exp

from ..base import BaseClient


class ScoreMixin(BaseClient):
    """
    score
    """

    def __init__(self): ...

    def score(self, semester: str | None = None):
        """
        score
        """
        is_gs = self.stu_type == StuType.GRADUATE
        project_id = 22 if is_gs else 1

        semester_id = None
        if semester is not None:
            if semester not in SEMESTER:
                raise DataError(f"Semester {semester} not found")
            else:
                semester_id = SEMESTER[semester]

        if semester_id is None:
            self._session.get(
                COURSETABLE_INDEX_URL_PATH, params={"projectId": project_id}
            )
            score_html = self._session.get(
                SCORE_HISTORY_URL_PATH,
                params={
                    "projectType": "MAJOR",  # ug not empty
                },
            ).text
        else:
            score_html = self._session.get(
                SCORE_SEARCH_URL_PATH,
                params={
                    "semesterId": semester_id,
                    "projectType": "MAJOR",  # can be empty (ug)
                },
            ).text
        try:
            score_dict = parse_score(html=score_html)
        except IndexError:
            raise HtmlParseError from None

        score_summary = GSScoreSummarys() if is_gs else UGScoreSummarys()
        score = GSScores() if is_gs else UGScores()

        if "summary" in score_dict:
            score_summary.load(data=score_dict["summary"])
            score_dict["summary"] = score_summary
        if "list" in score_dict:
            score.load(data=score_dict["list"])
            score_dict["list"] = score
        return score_dict

    def exp_score(self, semester: str | None = None):
        """
        experiments score
        """

        if semester is None:
            semester = self.semester
        if semester not in SEMESTER:
            raise DataError(f"Semester {semester} not found")
        semester_id = SEMESTER[semester]

        score_html = self._session.post(
            SCORE_EXP_URL_PATH,
            params={
                "semester.id": semester_id,
            },
        ).text

        try:
            score_list = parse_score_exp(html=score_html)
        except IndexError:
            raise HtmlParseError from None

        score = ExpScores()
        score.load(data=score_list)
        return score
