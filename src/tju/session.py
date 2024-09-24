"""
TJU session
"""

from __future__ import annotations

import os
import re

import ddddocr
import httpx

from .consts import (
    CAPTCHA_URL,
    DEFAULT_BASE_URL,
    HOME_URL_PATH,
    ID_URL_PATH,
    LOGIN_URL,
)
from .encrypt import ctx
from .exceptions import HtmlParseError, LoginError, SessionError
from .utils import HiddenPrints, get_current_semester, ua


class Session:
    """
    TJU Session
    """

    _client: httpx.Client
    _username: str
    _password: str
    _cache: dict

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        **kwargs,
    ):
        if username is None:
            username = os.environ.get("TJU_USER")
        if username is None:
            raise SessionError(
                "The `username` must be set either by passing `username` to the session or by setting the `TJU_USER` environment variable"
            )
        self._username = username

        if password is None:
            password = os.environ.get("TJU_PASS")
        if password is None:
            raise SessionError(
                "The `password` must be set either by passing `password` to the session or by setting the `TJU_PASS` environment variable"
            )
        self._password = password

        self._client = httpx.Client(
            follow_redirects=True,
            base_url=base_url,
            headers={"User-Agent": ua.random},
            **kwargs,
        )
        self._cache = {
            "stu_name": None,
            "stu_id": None,
            "semester": None,
            "is_gs": None,
            "has_minor": None,
        }

    def request(self, method: str, url: str, **kwargs):
        """
        Send a request.
        """
        return self._client.request(method=method, url=url, **kwargs)

    def get(self, url: str, **kwargs):
        """
        Send a GET request.
        """
        return self.request(method="GET", url=url, **kwargs)

    def post(self, url: str, **kwargs):
        """
        Send a POST request.
        """
        return self.request(method="POST", url=url, **kwargs)

    def login(self, username: str | None = None, password: str | None = None):
        """
        Session login
        """
        if username is None:
            username = self._username

        if password is None:
            password = self._password

        login_html = self.get(LOGIN_URL).text

        if re.findall(r"Log In Successful", login_html):
            return

        if re.findall(r"该网页目前只允许校内访问或您正在进行违规操作", login_html):
            raise LoginError("VPN not connected")

        try:
            s_exec = re.findall(r'name="execution" value="(.+?)"', login_html)[0]
        except Exception as e:
            raise HtmlParseError(f"{LOGIN_URL} HTML parse error") from e

        try:
            lt = re.findall(r'name="lt" value="(.+?)"', login_html)[0]
        except Exception as e:
            raise HtmlParseError(f"{LOGIN_URL} HTML parse error") from e

        captcha_html = self.get(CAPTCHA_URL)

        with HiddenPrints():
            ocr = ddddocr.DdddOcr()
            captcha = ocr.classification(captcha_html.content)

        rsa = ctx.call("strEnc", username + password + lt, "1", "2", "3")
        params = {
            "rsa": rsa,
            "ul": len(username),
            "pl": len(password),
            "lt": lt,
            "code": captcha,
            "execution": s_exec,
            "_eventId": "submit",
        }
        login_response = self.post(LOGIN_URL, params=params).text

        if re.findall(r"Please Login", login_response):
            raise LoginError("Login failed")

        home_html = self.get(HOME_URL_PATH).text
        home_info = re.findall(r'class="personal-name">\s(.*)\((\d+)\)', home_html)

        if len(home_info) == 0:
            raise HtmlParseError("HTML parse error")

        self._cache["stu_name"] = home_info[0][0]
        self._cache["stu_id"] = home_info[0][1]
        self._cache["semester"] = get_current_semester()

        id_html = self.post(ID_URL_PATH, params={"entityId": ""}).text
        self._cache["is_gs"] = "研究" in id_html
        self._cache["has_minor"] = "辅修" in id_html

        self._username = username
        self._password = password

    @property
    def stu_id(self) -> str:
        """
        student id
        """
        if "stu_id" not in self._cache or self._cache["stu_id"] is None:
            raise LoginError("Not login")
        return self._cache["stu_id"]

    @property
    def stu_name(self) -> str:
        """
        student name
        """
        if "stu_name" not in self._cache or self._cache["stu_name"] is None:
            raise LoginError("Not login")
        return self._cache["stu_name"]

    @property
    def semester(self) -> str:
        """
        semester
        """
        if "semester" not in self._cache or self._cache["semester"] is None:
            raise LoginError("Not login")
        return self._cache["semester"]

    @property
    def is_gs(self) -> bool:
        """
        is graduate student
        """
        if "is_gs" not in self._cache or self._cache["is_gs"] is None:
            raise LoginError("Not login")
        return self._cache["is_gs"]

    @property
    def has_minor(self) -> bool:
        """
        has minor (undergraduate)
        """
        if "has_minor" not in self._cache or self._cache["has_minor"] is None:
            raise LoginError("Not login")
        return self._cache["has_minor"]
