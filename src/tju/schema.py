from __future__ import annotations

from dataclasses import field


def mfield(data_key: str | None = None, **kwargs):
    # TODO: replace data_key
    return field(**kwargs)
