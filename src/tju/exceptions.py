"""
Library-specific exceptions raised by `tju`.

All exceptions are importable from ``tju.exceptions``.  Client code should
catch these rather than bare ``Exception`` so that errors are attributable to
the library layer.
"""


class SessionError(Exception):
    """Raised when the HTTP session cannot be created (e.g. missing credentials)."""


class HtmlParseError(Exception):
    """Raised when an EAMS HTML response does not match the expected structure."""


class LoginError(Exception):
    """Raised when the SSO CAS login fails (bad credentials or captcha failure)."""


class DataError(Exception):
    """Raised when returned data is structurally invalid or logically inconsistent."""


class StuTypeError(Exception):
    """Raised when an unsupported student type is passed to a client method."""
