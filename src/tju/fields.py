from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class Field:
    _key: str
    _raw_key: str
    _parse: Callable[[str], Any] = lambda x: x

    def parse(self, value):
        return self._parse(value)
