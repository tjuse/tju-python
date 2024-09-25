import re


def parse_profile(html):
    """
    parse personal profile
    """

    matches = re.findall(
        r'<td[ width="25%"]* class="title" style="width:18%">([^<]+)</td>\s*<td[^>]*>([^<]*)</td>',
        html,
    )
    result = {
        key.strip("：") if key.endswith("：") else key: value for key, value in matches
    }

    return result
