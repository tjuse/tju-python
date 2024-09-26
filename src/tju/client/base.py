"""
base client for client mixins
"""

from tju import Session
from tju.models import StuType


class BaseClient:
    """
    base client for client mixins
    """

    _session: Session

    @property
    def stu_id(self) -> str:
        """
        student id
        """
        ...

    @property
    def stu_name(self) -> str:
        """
        student name
        """
        ...

    @property
    def semester(self) -> str:
        """
        current semester
        """
        ...

    @property
    def stu_type(self) -> StuType:
        """
        student type
        """
        ...

    @property
    def has_minor(self) -> bool:
        """
        has minor (undergraduate)
        """
        ...
