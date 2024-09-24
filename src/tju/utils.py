import os
import sys
from datetime import datetime, timedelta, timezone

from fake_useragent import UserAgent

ua = UserAgent()


def get_current_semester():
    """
    current semester
    """
    now = datetime.now(tz=timezone(timedelta(hours=8)))
    year = now.year % 100
    month = now.month
    if month > 7:
        return f"{year}{year+1}1"
    if month < 2:
        return f"{year-1}{year}1"
    return f"{year-1}{year}2"


class HiddenPrints:
    def __enter__(self):
        self._original_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stdout = self._original_stdout
