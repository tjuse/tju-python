"""
client
"""

from tju import Session

from .base import BaseClient


class Client(BaseClient):
    """
    client for tju
    """

    _session: Session

    def __init__(self, session: Session):
        super().__init__()
        self._session = session

    @property
    def stu_id(self) -> str:
        return self._session.stu_id

    @property
    def stu_name(self) -> str:
        return self._session.stu_name

    @property
    def semester(self) -> str:
        return self._session.semester

    @property
    def stu_type(self) -> str:
        return "研究生" if self._session.is_gs else "本科生"

    @property
    def has_minor(self) -> bool:
        return self._session.has_minor
