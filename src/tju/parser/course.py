import itertools
import re

from tju.consts import CHINESE_WEEKDAY
from tju.exceptions import HtmlParseError


def _parse_arrange(html):
    result = []
    for each in html.strip().split("<br>"):
        each = each.strip() + " "  # for empty location
        if each.strip() == "":
            continue
        item = {}
        components = re.findall(
            r"(\S*)\s+星期(\S*)\s+(\d+)-(\d+)\s+(\S*)\s+(\S*)", each
        )[0]
        if len(components) < 6:
            raise HtmlParseError("HTML parse error")
        item["teacher"] = components[0].split(",")
        item["weekday"] = CHINESE_WEEKDAY[components[1]]
        item["unit"] = [_ for _ in range(int(components[2]), int(components[3]) + 1)]
        if "-" in components[4]:
            is_odd_week = "单" in components[4]
            is_even_week = "双" in components[4]
            weeks_str = components[4].replace("[", "").replace("]", "")
            if is_odd_week:
                weeks = weeks_str.replace("单", "").strip().split("-")
                item["week"] = [
                    _ for _ in range(int(weeks[0]), int(weeks[1]) + 1) if _ % 2 == 1
                ]
            elif is_even_week:
                weeks = weeks_str.replace("双", "").strip().split("-")
                item["week"] = [
                    _ for _ in range(int(weeks[0]), int(weeks[1]) + 1) if _ % 2 == 0
                ]
            else:
                weeks = weeks_str.strip().split("-")
                item["week"] = [_ for _ in range(int(weeks[0]), int(weeks[1]) + 1)]
        else:
            item["week"] = [int(components[4].strip())]
        item["location"] = components[5]
        result.append(item)
    return result


def parse_course(html):
    lession_id_and_arrange = re.findall(r"contents\['(.*)'\]='(.*)'", html)
    lession_id_to_arrange = dict(lession_id_and_arrange)
    keys_and_content = html.split('<th  class="gridselect-top" >')[1].split("</thead>")
    keys = re.findall(r"<th\s*[class]*.*>(.*)<\/th>", keys_and_content[0])
    keys = ["lession_id"] + keys
    content_and_tail = keys_and_content[1].split("</table>")
    content = re.findall(
        r'<tr><td.*value="(.*)"\s*type.*><\/td><td>(.*)<\/td><td>(.*)<\/td><td><a.*>(.*)<\/a><\/td><td>(.*\s?.*)\s?<\/td><td>(.*)<\/td><td>(.*)<\/td><td>(.*)<\/td><td>(.*)<\/td><td>(.*)<\/td><td>(.*)<\/td><td>(.*)\s?<\/td><td>(.*)<\/td>\s*<td>(.*)<\/td>\s*<td>(.*)<\/td>\s*<td>(.*)<\/td>',
        content_and_tail[0],
    )
    if len(content) != len(lession_id_to_arrange):
        raise HtmlParseError("HTML parse error")
    result = []
    for lession in content:
        item = {}
        for i, key in enumerate(keys):
            c = lession[i].strip()
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
            item[key] = c
        if item["lession_id"] not in lession_id_to_arrange:
            raise HtmlParseError("HTML parse error")
        item["arrange"] = _parse_arrange(lession_id_to_arrange[item["lession_id"]])
        del item["lession_id"]
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
