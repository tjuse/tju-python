import json
from datetime import date
from enum import Enum
from pathlib import Path

from tju.parser import (
    parse_course,
    parse_course_info,
    parse_exam,
    parse_exam_batch_id,
    parse_profile,
    parse_schedule,
    parse_score,
    parse_score_exp,
    parse_syllabus,
)


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
        .parent.joinpath("resources/parsed/parsed_profile_ug.json")
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
        .parent.joinpath("resources/parsed/parsed_schedule_ug_std.json")
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
        .parent.joinpath("resources/parsed/parsed_schedule_ug_class.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_course_1():
    raw_html = (
        Path(__file__).parent.joinpath("resources/website/course_ug_1.html").read_text()
    )
    result = parse_course(html=raw_html, semester="24251")
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_course_ug_1.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_course_2():
    raw_html = (
        Path(__file__).parent.joinpath("resources/website/course_ug_2.html").read_text()
    )
    result = parse_course(html=raw_html, semester="24251")
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_course_ug_2.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_course_info():
    raw_html = (
        Path(__file__).parent.joinpath("resources/website/course_info.html").read_text()
    )
    result = parse_course_info(raw_html)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_course_info.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_course_syllabus():
    raw_html = (
        Path(__file__)
        .parent.joinpath("resources/website/course_syllabus.html")
        .read_text()
    )
    result = parse_syllabus(raw_html)
    parsed = (
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_course_syllabus.md")
        .read_text()
    )

    assert result == parsed


def test_parse_exam_batch_id():
    raw_html = (
        Path(__file__).parent.joinpath("resources/website/exam_post.html").read_text()
    )
    result = parse_exam_batch_id(raw_html)
    assert result == "322"


def test_parse_exam():
    raw_html = Path(__file__).parent.joinpath("resources/website/exam.html").read_text()
    result = parse_exam(raw_html)
    parsed_list = json.loads(
        Path(__file__).parent.joinpath("resources/parsed/parsed_exam.json").read_text()
    )
    assert result == parsed_list


def test_parse_score_1():
    raw_html = (
        Path(__file__)
        .parent.joinpath("resources/website/score_search_ug.html")
        .read_text()
    )
    result = parse_score(raw_html)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_search_ug.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_score_2():
    raw_html = (
        Path(__file__)
        .parent.joinpath("resources/website/score_history_ug.html")
        .read_text()
    )
    result = parse_score(raw_html)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_history_ug.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_score_3():
    raw_html = (
        Path(__file__)
        .parent.joinpath("resources/website/score_search_gs.html")
        .read_text()
    )
    result = parse_score(raw_html)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_search_gs.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_score_4():
    raw_html = (
        Path(__file__)
        .parent.joinpath("resources/website/score_history_gs.html")
        .read_text()
    )
    result = parse_score(raw_html)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_history_gs.json")
        .read_text()
    )
    assert result == parsed_list


def test_parse_score_exp():
    raw_html = (
        Path(__file__).parent.joinpath("resources/website/score_exp.html").read_text()
    )
    result = parse_score_exp(raw_html)
    parsed_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_exp.json")
        .read_text()
    )
    assert result == parsed_list
