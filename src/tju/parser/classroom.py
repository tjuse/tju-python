from __future__ import annotations

import re

from tju.exceptions import DataError, HtmlParseError

# Server-side error messages returned by /eams/classroom/apply/free!search.action
_SERVER_ERRORS = {
    "借用教室小节错误": "借用教室小节错误: the EAMS class-period schedule is unavailable for the requested date/time (likely outside an active teaching week or project is unconfigured).",
    "请不要过快点击": "Rate-limited by EAMS: too many requests in a short time. Retry after a delay.",
    "对不起,您没有权限": "Permission denied (403): this account does not have access to the free classroom feature.",
}


def parse_free_classroom(html: str) -> list:
    """
    Parse the EAMS free-classroom search result HTML into a list of dicts.

    The result page is an EAMS gridtable fragment (no full <html> wrapper) loaded
    into the freeRoomList div by the browser.  It uses the same
    <thead><th>…</thead><tbody><tr><td>… structure as the exam and schedule tables.

    Raises:
        DataError: when the EAMS server returns a known error message
                   (e.g. "借用教室小节错误", rate-limit, permission denied).
        HtmlParseError: when the response looks like an unexpected HTML structure.
    """
    # Detect known server-side error responses before trying to parse
    for marker, message in _SERVER_ERRORS.items():
        if marker in html:
            raise DataError(message)

    keys_raw = re.findall(r"<th[^>]*>([\s\S]*?)</th>", html)
    keys = [re.sub(r"<[^>]+>", "", k).strip() for k in keys_raw]

    tbody_matches = re.findall(r"<tbody[\s\S]*?</tbody>", html)
    if not tbody_matches:
        # No tbody at all → may be an empty result page or unexpected format
        if "gridtable" not in html and "<th" not in html:
            raise HtmlParseError("Unexpected free classroom response: no grid table found.")
        return []

    tbody = tbody_matches[0]
    rows = re.findall(r"<tr[^>]*>([\s\S]*?)</tr>", tbody)

    classrooms = []
    for row in rows:
        cells = re.findall(r"<td[^>]*>([\s\S]*?)</td>", row)
        if not cells:
            continue
        # Strip inner HTML tags and whitespace from each cell
        values = [re.sub(r"<[^>]+>", "", c).strip() for c in cells]
        if not keys:
            classrooms.append({"row": values})
            continue
        if len(values) != len(keys):
            raise HtmlParseError(
                f"Free classroom column count mismatch: got {len(values)}, expected {len(keys)}"
            )
        classrooms.append(dict(zip(keys, values)))

    return classrooms
