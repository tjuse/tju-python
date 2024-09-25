import json
from pathlib import Path

from tju.parser.schedule import parse_schedule


def test_parse_schedule():
    raw_html = (
        Path(__file__)
        .parent.joinpath("resources/website/schedule_ug_std.html")
        .read_text()
    )
    result = parse_schedule(raw_html)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/response/parsed_schedule_ug_std.json")
        .read_text()
    )
    assert result == parsed_list
