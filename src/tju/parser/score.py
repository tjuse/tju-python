import re

from tju.exceptions import HtmlParseError


def parse_score(html, is_gs):
    """
    parse score
    """
    tables = html.split('<table class="gridtable">')
    if len(tables) < 2:
        raise HtmlParseError("Score data format Error")

    summary = []
    if len(tables) > 2:
        summary_keys_and_values = tables[1].split("</thead>")
        summary_keys = re.findall(r"<th>(.+?)<\/th>", summary_keys_and_values[0])
        summary_values_html = summary_keys_and_values[1].split("</tr>")
        for value_html in summary_values_html:
            values = re.findall(r"<th>(.+?)<\/th>", value_html)
            if not values:
                values = re.findall(r"<td>(.+?)<\/td>", value_html)
            if len(values) != len(summary_keys):
                continue
            summary.append(dict(zip(summary_keys, values)))
        courses_keys_and_values = tables[2].split("</thead>")
    else:
        courses_keys_and_values = tables[1].split("</thead>")

    courses_keys = re.findall(r"<th.*>(.+?)<\/th>", courses_keys_and_values[0])
    courses_values_html = courses_keys_and_values[1].split("</tr>")
    courses = []
    for value_html in courses_values_html:
        if "<td\n" in value_html:
            value_html = value_html.replace("<td\n", "<td>")
        sup_pattern = re.compile(r"(\S+)\t*<sup style=.*>(.*)</sup>")
        if sup_pattern.findall(value_html):
            value_html = re.sub(sup_pattern, r"\1 \2", value_html)
        values = re.findall(r"<td.*?>\s*(.*?)\s*<\/td>", value_html)
        if len(values) != len(courses_keys):
            continue
        courses.append(dict(zip(courses_keys, values)))
    return {"summary": summary, "list": courses}
