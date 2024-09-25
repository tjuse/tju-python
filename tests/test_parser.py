import json
from datetime import date
from enum import Enum
from pathlib import Path

from tju.parser import parse_profile, parse_schedule


def test_parse_profile():
    raw_html = (
        Path(__file__).parent.joinpath("resources/website/profile_ug.html").read_text()
    )
    result = parse_profile(raw_html)
    for k, v in result.items():
        if isinstance(v, date):
            result[k] = v.strftime("%Y-%m-%d")
        elif isinstance(v, Enum):
            result[k] = str(v)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/response/parsed_profile_ug.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_schedule_ug_std():
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


def test_parse_schedule_ug_class():
    raw_html = (
        Path(__file__)
        .parent.joinpath("resources/website/schedule_ug_class.html")
        .read_text()
    )
    result = parse_schedule(raw_html)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/response/parsed_schedule_ug_class.json")
        .read_text()
    )
    assert result == parsed_list
