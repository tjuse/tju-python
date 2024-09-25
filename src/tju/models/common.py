from enum import Enum


class StuType(Enum):
    """Student Type"""

    UNDERGRADUATE = "本科生"
    GRADUATE = "研究生"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Gender(Enum):
    """Gender"""

    MALE = "男"
    FEMALE = "女"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value
