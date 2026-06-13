"""tju — Python client for Tianjin University's SSO and EAMS systems.

Typical usage::

    from tju.client import create_client

    client = create_client()   # reads TJU_USER / TJU_PASS from env
    print(client.profile)
    print(client.schedule())
"""

from .session import Session as Session
