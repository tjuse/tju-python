"""HTML parser for the student personal-information (profile) page."""

import re
from typing import Any, Dict


def parse_profile(html) -> Dict[str, Any]:
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
