import json
from pathlib import Path

from tju.models.profile import Profile
from tju.models.schedule import ScheduleCourse


def test_schedule_schema():
    raw_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/response/parsed_schedule_ug_std.json")
        .read_text()
    )
    schema = ScheduleCourse.Schema(many=True)
    schedule_courses = schema.load(raw_list)
    assert schedule_courses is not None
    for raw_dict, schedule_course in zip(raw_list, schedule_courses):
        if "credit" in raw_dict:
            raw_dict["credit"] = float(raw_dict["credit"])
        assert all(getattr(schedule_course, k) == v for k, v in raw_dict.items())


def test_profile_schema():
    raw_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/response/parsed_profile_ug.json")
        .read_text()
    )
    profile = Profile(**raw_dict)
    assert profile is not None
    for k, v in raw_dict.items():
        assert getattr(profile, k) == v
