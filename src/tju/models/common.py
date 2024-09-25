from enum import Enum


class StuType(Enum):
    """Student Type"""

    UNDERGRADUATE = "本科生"
    GRADUATE = "研究生"

    def __str__(self):
        return self.value
