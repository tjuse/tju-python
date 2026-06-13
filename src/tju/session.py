"""
TJU session
"""

from __future__ import annotations

import os
import re
from typing import Optional

import ddddocr
import httpx

from .consts import (
    CAPTCHA_URL,
    DEFAULT_BASE_URL,
    HOME_URL_PATH,
    LOGIN_URL,
)
from .encrypt import ctx
from .exceptions import HtmlParseError, LoginError, SessionError
from .utils import FileTypes, HiddenPrints, ua


class Session:
    """
    TJU Session
    """

    _client: httpx.Client
    _username: str
    _password: str
    _cache: dict
    _session_file: Optional[FileTypes]

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
        self._cache = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._client.close()

    def request(
        self,
        method: str,
        url: str | httpx.URL,
        *,
        validate_session: bool = True,
        auto_renew: bool = True,
        **kwargs,
    ):
        """
        Send a request.
        """
        response = self._client.request(method=method, url=url, **kwargs)
        if validate_session and b"/cas/login?service=" in response.url.raw_path:
            if not auto_renew:
                raise SessionError("Session expired")
            self.get(LOGIN_URL, validate_session=False)
            if (
                b"/cas/login?service="
                in self.get(HOME_URL_PATH, validate_session=False).url.raw_path
            ):
                self.login()
            return self.request(
                method=method,
                url=url,
                validate_session=validate_session,
                auto_renew=False,
                **kwargs,
            )
        else:
            return response

    def get(
        self,
        url: str,
        *,
        validate_session: bool = True,
        auto_renew: bool = True,
        **kwargs,
    ):
        """
        Send a GET request.
        """
        return self.request(
            method="GET",
            url=url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs,
        )

    def post(
        self,
        url: str,
        *,
        validate_session: bool = True,
        auto_renew: bool = True,
        **kwargs,
    ):
        """
        Send a POST request.
        """
        return self.request(
            method="POST",
            url=url,
            validate_session=validate_session,
            auto_renew=auto_renew,
            **kwargs,
        )

    def login(self, username: str | None = None, password: str | None = None):
        """
        Session login
        """
        self._cache = {}

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

        self._username = username
        self._password = password

    def logout(self):
        """
        TODO: Session logout
        """
        raise NotImplementedError("Not implemented")

    @property
    def _cookies(self) -> httpx.Cookies:
        """
        TODO: cookies
        """
        return self._client.cookies
