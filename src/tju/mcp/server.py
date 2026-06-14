"""MCP server definition for the TJU EAMS client.

Exposes read-only EAMS queries as MCP tools over stdio.  The server
authenticates with the TJU SSO using credentials stored **locally** in the OS
keyring — the AI agent never sees the username or password on any tool surface.

Usage
-----
This module is imported by :func:`tju.mcp.main` after confirming that the
``mcp`` SDK is installed.  Direct use::

    from tju.mcp.server import build_server
    build_server().run()

Security guarantees
-------------------
* No tool accepts a username or password parameter.
* No tool returns a password value.
* Profile PII (student ID, phone, address …) is masked by default;
  revealing it requires a server-side config flag, not a tool argument.
* Transport is stdio-only — no network port is opened.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

import tju.config as cfg
from tju.exceptions import DataError, HtmlParseError, LoginError, SessionError
from tju.models import StuType

from .redact import mask_profile, should_reveal_pii

# ---------------------------------------------------------------------------
# Lazy client cache
# ---------------------------------------------------------------------------

_client_cache: Any = None  # tju.client.Client | None


def _get_client():
    """Return a cached :class:`~tju.client.Client`, logging in on first call.

    Raises :class:`RuntimeError` with a user-friendly message if no
    credentials are configured.
    """
    global _client_cache  # noqa: PLW0603

    if _client_cache is not None:
        return _client_cache

    username = cfg.get_username()
    if not username:
        raise RuntimeError(
            "No credentials found.  Run  tju-mcp setup  to store your "
            "TJU username and password in the OS keyring."
        )
    password = cfg.get_password(username)
    if not password:
        raise RuntimeError(
            f"No password found in the keyring for user '{username}'.  "
            "Run  tju-mcp setup  to re-enter your password."
        )

    # Import here to keep startup fast (ddddocr is expensive to load)
    from tju import Session  # noqa: PLC0415
    from tju.client import Client  # noqa: PLC0415

    session = Session(username=username, password=password)
    session.login()
    _client_cache = Client(session=session)
    return _client_cache


def _reset_client() -> None:
    """Clear the cached client (used in tests)."""
    global _client_cache  # noqa: PLW0603
    _client_cache = None


def _err(exc: Exception) -> str:
    """Format an exception as a plain string, never including credentials."""
    return f"[tju error] {type(exc).__name__}: {exc}"


# ---------------------------------------------------------------------------
# Server factory
# ---------------------------------------------------------------------------


def build_server(*, get_client=None) -> FastMCP:  # noqa: ANN001
    """Build and return the :class:`~mcp.server.fastmcp.FastMCP` instance.

    Args:
        get_client: Optional callable override for the client factory — used
                    in tests to inject a mock without network access.
    """
    _gc = get_client or _get_client

    mcp = FastMCP("tju")

    # ------------------------------------------------------------------
    # Tool: whoami
    # ------------------------------------------------------------------

    @mcp.tool()
    def whoami() -> dict[str, Any]:
        """Return basic identity information for the authenticated student.

        Includes: display name, student type (undergraduate / graduate),
        current semester code.  The student ID is masked unless the server's
        ``mcp_reveal_pii`` setting is enabled.

        No username or password is accepted or returned.
        """
        try:
            client = _gc()
            result: dict[str, Any] = {
                "stu_name": client.stu_name,
                "stu_type": client.stu_type.name,
                "semester": client.semester,
            }
            if should_reveal_pii():
                result["stu_id"] = client.stu_id
            else:
                from .redact import _partial_mask  # noqa: PLC0415
                result["stu_id"] = _partial_mask(client.stu_id)
            return result
        except (LoginError, SessionError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: get_profile
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_profile() -> dict[str, Any]:
        """Return the student's full profile from the EAMS personal-info page.

        Contains ~35 fields (name, faculty, major, enrollment dates, supervisory
        contacts, etc.).  Sensitive PII fields (student ID, phone, home address,
        email) are **masked by default**.  Set ``mcp_reveal_pii = true`` in
        ``~/.config/tju/config.toml`` or export ``TJU_MCP_REVEAL_PII=1`` on the
        server to reveal them.

        No username or password is accepted or returned.
        """
        try:
            client = _gc()
            from tju.models import Profile  # noqa: PLC0415
            profile = client.profile
            data = Profile.Schema().dump(profile)
            return mask_profile(data, reveal=should_reveal_pii())
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: get_schedule
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_schedule(semester: str | None = None) -> dict[str, Any]:
        """Return the personal timetable for the given semester.

        Args:
            semester: EAMS semester code, e.g. ``"24251"`` (2024-2025 first term).
                      Defaults to the current semester when omitted.

        Returns a list of course objects with name, credit, campus, weeks,
        teacher, and scheduled slots (weekday, units, location).
        """
        try:
            client = _gc()
            from tju.models.schedule import Course  # noqa: PLC0415
            schedule = client.schedule(semester=semester)
            courses = Course.Schema(many=True).dump(list(schedule))
            return {
                "semester": semester or client.semester,
                "count": len(courses),
                "courses": courses,
            }
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: get_exam
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_exam(semester: str | None = None) -> dict[str, Any]:
        """Return the exam schedule for the given semester.

        Args:
            semester: EAMS semester code (e.g. ``"24251"``).  Defaults to the
                      current semester when omitted.

        Returns a list of exam entries with course name, date, time, location,
        and seat number.
        """
        try:
            client = _gc()
            from tju.models.exam import Exam  # noqa: PLC0415
            exams = client.exam(semester=semester)
            rows = Exam.Schema(many=True).dump(list(exams))
            return {
                "semester": semester or client.semester,
                "count": len(rows),
                "exams": rows,
            }
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: get_scores
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_scores() -> dict[str, Any]:
        """Return the full academic score history.

        Detects student type (undergraduate / graduate) automatically and
        returns the appropriate score records with semester, course name,
        credit, score, and GPA (undergraduate) or exam status (graduate).
        """
        try:
            client = _gc()
            result = client.score()
            is_gs = client.stu_type == StuType.GRADUATE
            score_list = result.get("list", [])
            if is_gs:
                from tju.models.score import GSScore  # noqa: PLC0415
                rows = GSScore.Schema(many=True).dump(list(score_list))
            else:
                from tju.models.score import UGScore  # noqa: PLC0415
                rows = UGScore.Schema(many=True).dump(list(score_list))
            return {
                "student_type": "graduate" if is_gs else "undergraduate",
                "count": len(rows),
                "scores": rows,
            }
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: get_exp_scores
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_exp_scores(semester: str) -> dict[str, Any]:
        """Return experiment / lab course scores for the given semester.

        Args:
            semester: EAMS semester code (e.g. ``"24251"``).  Required.

        Returns a list of experiment score records with project name,
        sub-scores, and final project score.
        """
        try:
            client = _gc()
            from tju.models.score import ExpScore  # noqa: PLC0415
            exp = client.exp_score(semester=semester)
            rows = ExpScore.Schema(many=True).dump(list(exp))
            return {
                "semester": semester,
                "count": len(rows),
                "scores": rows,
            }
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: query_courses
    # ------------------------------------------------------------------

    @mcp.tool()
    def query_courses(
        semester: str | None = None,
        graduate: bool | None = None,
    ) -> dict[str, Any]:
        """Query the public course library.

        Args:
            semester: EAMS semester code (defaults to current semester).
            graduate: ``True`` for the graduate course library, ``False`` for
                      undergraduate.  Defaults to the student's own type.

        Returns a list of courses with name, credit, campus, teacher,
        enrollment limit, and syllabus availability.
        """
        try:
            client = _gc()
            from tju.models.course import LibCourse  # noqa: PLC0415
            stu_type: StuType | None = None
            if graduate is True:
                stu_type = StuType.GRADUATE
            elif graduate is False:
                stu_type = StuType.UNDERGRADUATE
            courses = client.query_courses(semester=semester, stu_type=stu_type)
            rows = LibCourse.Schema(many=True).dump(list(courses))
            return {
                "semester": semester or client.semester,
                "count": len(rows),
                "courses": rows,
            }
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: get_course_info
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_course_info(lesson_id: str) -> dict[str, Any]:
        """Return metadata for a specific course (semester, faculty, lesson ID).

        Args:
            lesson_id: The EAMS lesson ID (``lession_id`` field from
                       :func:`query_courses`).
        """
        try:
            client = _gc()
            info = client.query_course_info(lession_id=lesson_id)
            # info is a raw dict from the parser
            return {"lesson_id": lesson_id, "info": info}
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: get_syllabus
    # ------------------------------------------------------------------

    @mcp.tool()
    def get_syllabus(lesson_id: str) -> dict[str, Any]:
        """Return the course syllabus as a Markdown string.

        Args:
            lesson_id: The EAMS lesson ID (``lession_id`` field from
                       :func:`query_courses`).
        """
        try:
            client = _gc()
            md = client.query_syllabus(lession_id=lesson_id)
            return {"lesson_id": lesson_id, "syllabus_markdown": md}
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    # ------------------------------------------------------------------
    # Tool: search_free_classrooms
    # ------------------------------------------------------------------

    @mcp.tool()
    def search_free_classrooms(
        date_begin: str,
        date_end: str | None = None,
        campus_id: str | None = None,
        time_begin: str = "1",
        time_end: str = "12",
        seats: int | None = None,
        name: str | None = None,
    ) -> dict[str, Any]:
        """Search for available classrooms on a given date and time range.

        Args:
            date_begin:  Start date in ``YYYY-MM-DD`` format (required).
            date_end:    End date; defaults to ``date_begin`` (single-day).
            campus_id:   Campus filter: ``"2"`` 卫津路, ``"3"`` 北洋园.
                         Leave ``null`` to search all campuses.
            time_begin:  Start class-unit (1–12, default ``"1"``).
            time_end:    End class-unit (1–12, default ``"12"``).
            seats:       Minimum seat count filter (optional).
            name:        Classroom name substring filter (optional).

        Returns a list of free classrooms with campus, building, room name,
        type, and seat count.
        """
        try:
            client = _gc()
            from tju.models.classroom import FreeClassroom  # noqa: PLC0415
            classrooms = client.free_classrooms(
                date_begin=date_begin,
                date_end=date_end,
                campus_id=campus_id,
                time_begin=time_begin,
                time_end=time_end,
                seats=seats,
                name=name,
            )
            rows = FreeClassroom.Schema(many=True).dump(list(classrooms))
            return {
                "date_begin": date_begin,
                "date_end": date_end or date_begin,
                "count": len(rows),
                "classrooms": rows,
            }
        except (LoginError, SessionError, DataError, HtmlParseError) as exc:
            return {"error": _err(exc)}
        except RuntimeError as exc:
            return {"error": str(exc)}

    return mcp
