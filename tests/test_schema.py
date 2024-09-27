import json
from pathlib import Path

from tju.models.course import CourseLib, LibCourse
from tju.models.exam import Exam, Exams
from tju.models.profile import Profile
from tju.models.schedule import Course, Schedule
from tju.models.score import Score, Scores, ScoreSummary, ScoreSummarys


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
    schedule = Schedule()
    schedule.load(data=raw_list)
    assert schedule is not None
    for serialized_dict, course in zip(serialized_list, schedule):
        if "credit" in serialized_dict:
            serialized_dict["credit"] = float(serialized_dict["credit"])
        course_dict = Course.Schema().dump(course)
        assert course_dict == serialized_dict


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
    profile = Profile.Schema().load(raw_dict)
    assert profile is not None
    profile_dict = Profile.Schema().dump(profile)
    assert profile_dict == serialized_dict


def test_course_schema():
    raw_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_course_ug.json")
        .read_text()
    )
    serialized_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_course_ug.json")
        .read_text()
    )
    for k, v in serialized_dict.items():
        if k == "list":
            continue
        assert raw_dict[k] == v
    raw_list = raw_dict["list"]
    serialized_list = serialized_dict["list"]
    courses = CourseLib()
    courses.load(data=raw_list)
    assert courses is not None
    for serialized_dict, course in zip(serialized_list, courses):
        course_dict = LibCourse.Schema().dump(course)
        assert course_dict == serialized_dict


def test_exam_schema():
    raw_list = json.loads(
        Path(__file__).parent.joinpath("resources/parsed/parsed_exam.json").read_text()
    )
    serialized_list = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_exam.json")
        .read_text()
    )
    exams = Exams()
    exams.load(data=raw_list)
    assert exams is not None
    for serialized_dict, exam in zip(serialized_list, exams):
        exam_dict = Exam.Schema().dump(exam)
        assert exam_dict == serialized_dict


def test_score_schema_1():
    raw_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_search_ug.json")
        .read_text()
    )
    serialized_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_score_search_ug.json")
        .read_text()
    )
    raw_list = raw_dict["list"]
    serialized_list = serialized_dict["list"]
    scores = Scores()
    scores.load(data=raw_list)
    assert scores is not None
    for serialized_dict, score in zip(serialized_list, scores):
        score_dict = Score.Schema().dump(score)
        assert score_dict == serialized_dict


def test_score_schema_2():
    raw_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_history_ug.json")
        .read_text()
    )
    serialized_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_score_history_ug.json")
        .read_text()
    )

    raw_score_list = raw_dict["list"]
    serialized_score_list = serialized_dict["list"]
    scores = Scores()
    scores.load(data=raw_score_list)
    assert scores is not None
    scores_list = Score.Schema(many=True).dump(scores)
    assert scores_list == serialized_score_list

    raw_summary_list = raw_dict["summary"]
    serialized_summary_list = serialized_dict["summary"]
    summarys = ScoreSummarys()
    summarys.load(data=raw_summary_list)
    assert summarys is not None
    summarys_list = ScoreSummary.Schema(many=True).dump(summarys)
    assert summarys_list == serialized_summary_list


def test_score_schema_3():
    raw_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_search_gs.json")
        .read_text()
    )
    serialized_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_score_search_gs.json")
        .read_text()
    )

    raw_score_list = raw_dict["list"]
    serialized_score_list = serialized_dict["list"]
    scores = Scores()
    scores.load(data=raw_score_list)
    assert scores is not None
    scores_list = Score.Schema(many=True).dump(scores)
    assert scores_list == serialized_score_list

    raw_summary_list = raw_dict["summary"]
    serialized_summary_list = serialized_dict["summary"]
    summarys = ScoreSummarys()
    summarys.load(data=raw_summary_list)
    assert summarys is not None
    summarys_list = ScoreSummary.Schema(many=True).dump(summarys)
    assert summarys_list == serialized_summary_list


def test_score_schema_4():
    raw_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/parsed/parsed_score_history_gs.json")
        .read_text()
    )
    serialized_dict = json.loads(
        Path(__file__)
        .parent.joinpath("resources/serialized/serialized_score_history_gs.json")
        .read_text()
    )

    raw_score_list = raw_dict["list"]
    serialized_score_list = serialized_dict["list"]
    scores = Scores()
    scores.load(data=raw_score_list)
    assert scores is not None
    scores_list = Score.Schema(many=True).dump(scores)
    assert scores_list == serialized_score_list

    raw_summary_list = raw_dict["summary"]
    serialized_summary_list = serialized_dict["summary"]
    summarys = ScoreSummarys()
    summarys.load(data=raw_summary_list)
    assert summarys is not None
    summarys_list = ScoreSummary.Schema(many=True).dump(summarys)
    print(summarys_list)
    assert summarys_list == serialized_summary_list
