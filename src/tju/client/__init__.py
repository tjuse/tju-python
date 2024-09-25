"""
client
"""

import re

from tju import Session
from tju.client.api import ScheduleMixin
from tju.consts import HOME_URL_PATH, ID_URL_PATH
from tju.exceptions import HtmlParseError
from tju.models.common import StuType
from tju.utils import get_current_semester

from .base import BaseClient


class Client(ScheduleMixin, BaseClient):
    """
    client for tju
    """

    _session: Session

    def __init__(self, session: Session):
        super().__init__()
        self._session = session

    @property
    def stu_id(self) -> str:
        """Get student id from current session"""
        if "stu_id" not in self._session._cache:
            home_html = self._session.get(HOME_URL_PATH).text
            home_info = re.findall(r'class="personal-name">\s(.*)\((\d+)\)', home_html)

            if len(home_info) == 0:
                raise HtmlParseError("HTML parse error")

            self._session._cache["stu_name"] = home_info[0][0]
            self._session._cache["stu_id"] = home_info[0][1]
        return self._session._cache["stu_id"]

    @property
    def stu_name(self) -> str:
        """Get student name from current session"""
        if "stu_name" not in self._session._cache:
            home_html = self._session.get(HOME_URL_PATH).text
            home_info = re.findall(r'class="personal-name">\s(.*)\((\d+)\)', home_html)

            if len(home_info) == 0:
                raise HtmlParseError("HTML parse error")

            self._session._cache["stu_name"] = home_info[0][0]
            self._session._cache["stu_id"] = home_info[0][1]
        return self._session._cache["stu_name"]

    @property
    def semester(self) -> str:
        if "semester" not in self._session._cache:
            self._session._cache["semester"] = get_current_semester()
        return self._session._cache["semester"]

    @property
    def stu_type(self) -> StuType:
        if "is_gs" not in self._session._cache:
            id_html = self._session.post(ID_URL_PATH, params={"entityId": ""}).text
            self._session._cache["is_gs"] = "研究" in id_html
            self._session._cache["has_minor"] = "辅修" in id_html
        return (
            StuType.GRADUATE if self._session._cache["is_gs"] else StuType.UNDERGRADUATE
        )

    @property
    def has_minor(self) -> bool:
        if "is_gs" not in self._session._cache:
            id_html = self._session.post(ID_URL_PATH, params={"entityId": ""}).text
            self._session._cache["is_gs"] = "研究" in id_html
            self._session._cache["has_minor"] = "辅修" in id_html
        return self._session._cache["has_minor"]


def create_client(*args, **kwargs) -> Client:
    session = Session(*args, **kwargs)
    return Client(session=session)
