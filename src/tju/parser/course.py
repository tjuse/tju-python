import itertools
import re

from markdownify import markdownify as md

from tju.consts import CHINESE_WEEKDAY
from tju.exceptions import HtmlParseError


def _parse_week(html):
    if "," in html:
        weeks = html.split(",")
    else:
        weeks = [html]
    result = []
    for week in weeks:
        if "-" in week:
            is_odd_week = "单" in week
            is_even_week = "双" in week
            weeks_str = week.replace("[", "").replace("]", "")
            if is_odd_week:
                weeks = weeks_str.replace("单", "").strip().split("-")
                result.extend(
                    [_ for _ in range(int(weeks[0]), int(weeks[1]) + 1) if _ % 2 == 1]
                )
            elif is_even_week:
                weeks = weeks_str.replace("双", "").strip().split("-")
                result.extend(
                    [_ for _ in range(int(weeks[0]), int(weeks[1]) + 1) if _ % 2 == 0]
                )
            else:
                weeks = weeks_str.strip().split("-")
                result.extend([_ for _ in range(int(weeks[0]), int(weeks[1]) + 1)])
        else:
            result.extend([int(week.strip())])
    return sorted(result)


def _parse_arrange(html):
    result = []
    for each in html.strip().split("<br>"):
        each = each.strip() + " "  # for empty location
        if each.strip() == "":
            continue
        item = {}
        components = re.findall(
            r"(.*)\s*星期(\S*)\s+(\d+)-(\d+)\s+(\S*)\s+(\S*)", each
        )[0]
        components = [_.strip() for _ in components]
        if len(components) < 6:
            raise HtmlParseError("HTML parse error")
        item["teacher"] = components[0].split(",") if components[0] else []
        item["weekday"] = CHINESE_WEEKDAY[components[1]]
        item["unit"] = [_ for _ in range(int(components[2]), int(components[3]) + 1)]
        item["week"] = _parse_week(components[4])
        item["location"] = components[5]
        result.append(item)
    return result


def parse_course(html, semester: str):
    lession_id_and_arrange = re.findall(r"contents\['(.*)'\]='(.*)'", html)
    lession_id_to_arrange = dict(lession_id_and_arrange)
    keys_and_content = html.split('<th  class="gridselect-top" >')[1].split("</thead>")
    keys = re.findall(r"<th\s*[class]*.*>(.*)<\/th>", keys_and_content[0])
    keys = ["lession_id"] + keys
    content_and_tail = keys_and_content[1].split("</table>")

    # fix ,\n
    content_and_tail[0] = content_and_tail[0].replace(",\n", ",")
    # fix <sup> tag
    sup_pattern = re.compile(r">(\S+)<\/a>\s*<sup.*>(\S+)<\/sup>\s")
    if sup_pattern.findall(content_and_tail[0]):
        content_and_tail[0] = re.sub(sup_pattern, r">\1 \2</a>", content_and_tail[0])

    # Build row regex dynamically so it works regardless of column count.
    # Old EAMS HTML had 16 columns; newer versions dropped 4 enrollment columns (12 columns).
    # Pattern: checkbox TD (captures lession_id value) + n_data data TDs captured individually.
    n_data = len(keys) - 1  # number of data TDs per row (excludes the lession_id column)
    row_pattern = re.compile(
        r"<tr>\s*<td[^>]*>"
        r'<input[^>]*\bvalue="(\d+)"[^>]*/>'
        r"</td>"
        + (r"\s*<td[^>]*>([\s\S]*?)</td>") * n_data
    )
    content = row_pattern.findall(content_and_tail[0])

    result = []
    for lession in content:
        item = {}
        item["semester"] = semester
        for i, key in enumerate(keys):
            raw = lession[i]
            # Extract text content: prefer anchor text if present, otherwise strip all HTML tags.
            a_match = re.search(r"<a[^>]*>([\s\S]*?)<\/a>", raw)
            if a_match:
                c = a_match.group(1).strip()
            else:
                c = re.sub(r"<[^>]+>", "", raw).strip()
            if key == "教学班":
                if c.startswith("班级:"):
                    c = c.replace("班级:", "").strip()
                c = [_.split(";") for _ in c.split(" ")]
                c = list(itertools.chain(*c))
            elif key == "教师":
                c = c.split(",")
            elif key == "课程类别":
                c = [_.strip() for _ in c.split(",")]
            elif key == "学时/周":
                item["总学时"] = c.split("/")[0]
                item["周学时"] = c.split("/")[1]
                continue
            elif key == "课程名称":
                c = c.replace("\n", "")
            item[key] = c
        # Some courses (e.g. thesis supervision, online-only) have no timetable JS entry.
        arrange_html = lession_id_to_arrange.get(item["lession_id"], "")
        item["arrange"] = _parse_arrange(arrange_html) if arrange_html.strip() else []
        result.append(item)

    numbers = re.findall(r"pageInfo\((\d+),(\d+),(\d+)\)", content_and_tail[1])[0]
    page_from = int(numbers[0])
    page_to = int(numbers[1])
    total = int(numbers[2])
    page_size = page_to - page_from + 1
    page_no = (page_from - 1) // page_size + 1
    return {
        "list": result,
        "page_no": page_no,
        "page_size": page_size,
        "total": total,
    }


def parse_course_info(html):
    semester = re.findall(r"学期:</td>\s+<td.*>(.*)</td>", html)[0]
    faculty = re.findall(r"开课院系:</td>\s+<td.*>(.*)</td>", html)[0]
    result = {
        "semester": semester,
        "faculty": faculty,
    }
    return result


def parse_syllabus(html):
    return md(html).replace("\n\n\n", "\n\n").strip()
