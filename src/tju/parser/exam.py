import re

from tju.exceptions import HtmlParseError


def parse_exam_batch_id(html):
    """
    parse exam post
    """
    return re.findall(r"examBatch.id=(\d+)", html)[0]


def parse_exam(html):
    """
    parse exam
    """
    exams = []

    keys = re.findall(r"<th.*>(.+?)</th.*>", html)
    tbody = re.findall(r"<tbody([\s\S]+?)</tbody>", html)[0]
    courses = re.findall(r"<tr>([\s\S]+?)</tr>", tbody)
    for course in courses:
        arr = re.findall(r"<td>([\s\S]+?)</td>", course)
        if not arr:
            continue
        arr = list(
            map(lambda x: re.findall(r">(.+?)</font", x)[0] if "color" in x else x, arr)
        )
        if len(arr) != len(keys):
            raise HtmlParseError("Failed to parse exam")
        item = {k.strip(): v.strip() for k, v in zip(keys, arr)}
        exams.append(item)
    return exams
