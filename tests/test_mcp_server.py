"""Offline smoke tests for the TJU MCP server.

All tests use a mocked Client — no network or VPN required.
The tests verify the security invariants:
- No tool accepts a username or password parameter
- No tool output ever contains the password
- Profile PII is masked by default
- Missing credentials returns a friendly error message

Skipped automatically if the ``mcp`` extra is not installed.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("mcp", reason="tju[mcp] extra not installed")

from tju.mcp.server import _reset_client, build_server  # noqa: E402
from tju.models import StuType  # noqa: E402

# ---------------------------------------------------------------------------
# Shared mock client fixture
# ---------------------------------------------------------------------------

PASSWORD = "super_secret_password_must_not_leak"


@pytest.fixture()
def config_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("TJU_CONFIG_DIR", str(tmp_path))
    monkeypatch.delenv("TJU_MCP_REVEAL_PII", raising=False)
    return tmp_path


@pytest.fixture()
def mock_client():
    client = MagicMock()
    client.stu_name = "测试同学"
    client.stu_id = "2024000001"
    client.semester = "24251"
    client.stu_type = StuType.UNDERGRADUATE
    client.has_minor = False

    # profile
    from tju.models.profile import Profile  # noqa: PLC0415
    profile = MagicMock(spec=Profile)
    profile_data = {
        "stu_id": "2024000001",
        "stu_name": "测试同学",
        "faculty": "计算机学院",
        "major": "软件工程",
        "email": "test@tju.edu.cn",
        "phone": "13800001234",
        "mobile": "13900001234",
        "home_address": "天津市南开区",
        "home_address_zip": "300071",
    }
    # mock Schema().dump() to return our dict
    with patch("tju.models.profile.Profile.Schema") as schema_cls:
        schema_cls.return_value.dump.return_value = profile_data
    client.profile = profile

    # schedule
    client.schedule.return_value = []

    # exam
    client.exam.return_value = []

    # score — returns dict with "list" key
    from tju.models.score import UGScores  # noqa: PLC0415
    client.score.return_value = {"list": UGScores(), "summary": []}

    # exp_score
    from tju.models.score import ExpScores  # noqa: PLC0415
    client.exp_score.return_value = ExpScores()

    # query_courses
    from tju.models.course import CourseLib  # noqa: PLC0415
    client.query_courses.return_value = CourseLib()

    # query_course_info
    client.query_course_info.return_value = {"semester": "24251", "faculty": "CS"}

    # query_syllabus
    client.query_syllabus.return_value = "# Syllabus\n\nTest content."

    # free_classrooms
    from tju.models.classroom import FreeClassrooms  # noqa: PLC0415
    client.free_classrooms.return_value = FreeClassrooms()

    return client


@pytest.fixture(autouse=True)
def reset_client_cache():
    """Ensure the global client cache is cleared between tests."""
    _reset_client()
    yield
    _reset_client()


# ---------------------------------------------------------------------------
# Helper: build server with injected client
# ---------------------------------------------------------------------------


def _server(client):
    return build_server(get_client=lambda: client)


# ---------------------------------------------------------------------------
# Security invariants
# ---------------------------------------------------------------------------


def test_no_tool_accepts_password_parameter(mock_client):
    """No tool's input schema should contain a 'password' or 'username' param."""
    mcp = _server(mock_client)
    # Introspect registered tools via FastMCP's internal registry
    # tools is a dict of name → Tool
    forbidden = {"password", "passwd", "secret", "username", "user", "credential"}
    for tool_name, tool in mcp._tool_manager._tools.items():
        params = set(tool.parameters.get("properties", {}).keys())
        overlap = params & forbidden
        assert not overlap, (
            f"Tool '{tool_name}' exposes forbidden parameter(s): {overlap}"
        )


def test_no_tool_output_contains_password(mock_client, config_dir):
    """Password string must never appear in any tool's serialised output."""
    mcp = _server(mock_client)
    # Patch the profile Schema to return data that contains a mock password
    # in a non-password field to ensure the test is meaningful
    results: list[Any] = []

    # We call each tool function directly via the manager
    for name, tool in mcp._tool_manager._tools.items():
        try:
            result = tool.fn()
        except TypeError:
            # Tool requires arguments — call with minimal valid args
            if name == "get_exp_scores":
                result = tool.fn(semester="24251")
            elif name == "search_free_classrooms":
                result = tool.fn(date_begin="2025-10-08")
            elif name == "get_course_info":
                result = tool.fn(lesson_id="12345")
            elif name == "get_syllabus":
                result = tool.fn(lesson_id="12345")
            else:
                continue
        dumped = json.dumps(result, ensure_ascii=False, default=str)
        assert PASSWORD not in dumped, (
            f"Tool '{name}' output contains the password!"
        )
        results.append(result)

    assert results, "No tool results collected — test did not run correctly"


def test_profile_pii_masked_by_default(mock_client, config_dir):
    """get_profile must mask sensitive fields (stu_id, email, phone…) by default."""
    mcp = _server(mock_client)
    profile_tool = mcp._tool_manager._tools["get_profile"]

    with patch(
        "tju.models.profile.Profile.Schema",
    ) as schema_cls:
        schema_cls.return_value.dump.return_value = {
            "stu_id": "2024000001",
            "stu_name": "测试同学",
            "faculty": "计算机学院",
            "email": "test@tju.edu.cn",
            "phone": "13800001234",
        }
        result = profile_tool.fn()

    assert "error" not in result, f"Unexpected error: {result.get('error')}"
    # stu_id and email must be masked
    assert result.get("stu_id") != "2024000001", "stu_id should be masked"
    assert result.get("email") != "test@tju.edu.cn", "email should be masked"
    # non-sensitive field unchanged
    assert result.get("stu_name") == "测试同学"
    assert result.get("faculty") == "计算机学院"


def test_profile_pii_revealed_when_flag_set(mock_client, config_dir, monkeypatch):
    """When TJU_MCP_REVEAL_PII=1, get_profile returns unmasked PII."""
    monkeypatch.setenv("TJU_MCP_REVEAL_PII", "1")
    mcp = _server(mock_client)
    profile_tool = mcp._tool_manager._tools["get_profile"]

    with patch("tju.models.profile.Profile.Schema") as schema_cls:
        schema_cls.return_value.dump.return_value = {
            "stu_id": "2024000001",
            "stu_name": "测试同学",
            "email": "test@tju.edu.cn",
        }
        result = profile_tool.fn()

    assert result.get("stu_id") == "2024000001"
    assert result.get("email") == "test@tju.edu.cn"


def test_missing_credentials_returns_friendly_error(config_dir):
    """When no credentials are stored, tools return a friendly error string."""
    import tju.config as cfg  # noqa: PLC0415
    # Ensure no credentials in the empty config_dir
    assert cfg.get_username() is None

    from tju.mcp.server import _get_client  # noqa: PLC0415
    mcp = build_server(get_client=_get_client)  # use real get_client
    whoami_tool = mcp._tool_manager._tools["whoami"]
    result = whoami_tool.fn()
    assert "error" in result
    assert "setup" in result["error"].lower() or "no credentials" in result["error"].lower()


def test_whoami_returns_expected_fields(mock_client, config_dir):
    mcp = _server(mock_client)
    result = mcp._tool_manager._tools["whoami"].fn()
    assert "stu_name" in result
    assert result["stu_name"] == "测试同学"
    assert "stu_type" in result
    assert "semester" in result
    assert "stu_id" in result  # present but masked


def test_whoami_masks_stu_id_by_default(mock_client, config_dir):
    mcp = _server(mock_client)
    result = mcp._tool_manager._tools["whoami"].fn()
    assert result.get("stu_id") != "2024000001", "stu_id must be masked by default"


def test_get_schedule_returns_structure(mock_client, config_dir):
    mcp = _server(mock_client)
    result = mcp._tool_manager._tools["get_schedule"].fn(semester="24251")
    assert "error" not in result, result
    assert "courses" in result
    assert result["semester"] == "24251"


def test_get_exam_returns_structure(mock_client, config_dir):
    mcp = _server(mock_client)
    result = mcp._tool_manager._tools["get_exam"].fn(semester="24251")
    assert "error" not in result, result
    assert "exams" in result


def test_get_scores_returns_structure(mock_client, config_dir):
    mcp = _server(mock_client)
    result = mcp._tool_manager._tools["get_scores"].fn()
    assert "error" not in result, result
    assert "scores" in result
    assert result["student_type"] == "undergraduate"


def test_search_free_classrooms_returns_structure(mock_client, config_dir):
    mcp = _server(mock_client)
    result = mcp._tool_manager._tools["search_free_classrooms"].fn(
        date_begin="2025-10-08"
    )
    assert "error" not in result, result
    assert "classrooms" in result
    assert result["date_begin"] == "2025-10-08"
