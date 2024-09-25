import json
from pathlib import Path

from tju.models.course import LibCourse
from tju.models.profile import Profile
from tju.models.schedule import Course


def test_schedule_schema():
    raw_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_schedule_ug_std.json")
        .read_text()
    )
    serialized_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_schedule_ug_std.json")
        .read_text()
    )
    schema = Course.Schema(many=True)
    courses = schema.load(raw_list)
    assert courses is not None
    for serialized_dict, course in zip(serialized_list, courses):
        if "credit" in serialized_dict:
            serialized_dict["credit"] = float(serialized_dict["credit"])
        for k, v in serialized_dict.items():
            if k == "arrange":
                for i, arrange in enumerate(v):
                    for k, v in arrange.items():
                        assert getattr(course.arrange[i], k) == v
            else:
                assert getattr(course, k) == v


def test_profile_schema():
    raw_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_profile_ug.json")
        .read_text()
    )
    serialized_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_profile_ug.json")
        .read_text()
    )
    schema = Profile.Schema()
    profile = schema.load(raw_dict)
    assert profile is not None
    for k, v in serialized_dict.items():
        assert getattr(profile, k) == v


def test_course_schema():
    raw_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_course_ug.json")
        .read_text()
    )
    serialized_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_course.json")
        .read_text()
    )
    schema = LibCourse.Schema(many=True)
    courses = schema.load(raw_list)
    assert courses is not None
    for serialized_dict, course in zip(serialized_list, courses):
        if "credit" in serialized_dict:
            serialized_dict["credit"] = float(serialized_dict["credit"])
        for k, v in serialized_dict.items():
            if k == "arrange":
                for i, arrange in enumerate(v):
                    for k, v in arrange.items():
                        assert getattr(course.arrange[i], k) == v
            else:
                assert getattr(course, k) == v
