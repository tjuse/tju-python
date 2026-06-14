"""Main application screen — lazygit-style two-pane layout.

Left:  a bordered *menu* panel (navigation list).
Right: a bordered *content* panel that shows the data for the selected item.

Design notes
------------
* The active panel is highlighted via the ``:focus-within`` CSS rule, so the
  border colour follows keyboard focus (like lazygit).
* Content is swapped **asynchronously**: ``await body.remove_children()`` is
  awaited *before* mounting new widgets.  Textual's ``remove()`` is deferred,
  so mounting fixed-id widgets without awaiting the removal first raises
  ``DuplicateIds`` — awaiting removal is the fix.
* Worker threads only ever fetch/serialise raw data and hand it back to the
  main thread via ``call_from_thread``; all widget creation happens on the
  event-loop thread.
"""

from __future__ import annotations

from textual import work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Footer, Input, ListItem, ListView, LoadingIndicator, Static

from tju.client import Client
from tju.exceptions import DataError, HtmlParseError
from tju.models import StuType

from tju import config as cfg
from ..widgets import VimListView
from ..render import (
    render_classrooms,
    render_courses,
    render_exam,
    render_exp_scores,
    render_gs_scores,
    render_profile,
    render_schedule,
    render_ug_scores,
)

# ---------------------------------------------------------------------------
# Sidebar menu items:  (action_id, label, icon)
# ---------------------------------------------------------------------------

_ACTIONS: list[tuple[str, str, str]] = [
    ("profile",    "个人信息",  "󰀄"),
    ("schedule",   "课表",      "󰃭"),
    ("scores",     "成绩",      "󰄕"),
    ("exam",       "考试安排",  "󰸞"),
    ("exp_scores", "实验成绩",  "󰂖"),
    ("courses",    "课程库",    "󰂺"),
    ("classrooms", "空闲教室",  "󱂵"),
    ("settings",   "设置",      "󰒓"),
    ("logout",     "退出登录",  "󰍃"),
]


class MainScreen(Screen):
    """Two-pane main screen with lazygit-style navigation."""

    BINDINGS = [
        Binding("tab", "toggle_panel", "切换面板", show=True),
        Binding("r", "refresh", "刷新", show=True),
        Binding("escape", "focus_menu", "返回菜单", show=False),
        Binding("h", "focus_menu", "菜单", show=False),
        Binding("l", "focus_content", "内容", show=False),
    ]

    _current_action: str = ""
    _request_id: int = 0

    # ------------------------------------------------------------------
    # Compose
    # ------------------------------------------------------------------

    def compose(self) -> ComposeResult:
        with Horizontal(id="body"):
            menu = Vertical(id="menu-panel")
            menu.border_title = "菜单"
            menu.border_subtitle = "j/k 移动"
            with menu:
                yield VimListView(
                    *[
                        ListItem(Static(f" {icon}  {label}"), id=f"item-{aid}")
                        for aid, label, icon in _ACTIONS
                    ],
                    id="menu",
                )
            content = Vertical(id="content-panel")
            content.border_title = "TJU"
            with content:
                yield VerticalScroll(
                    Static("\n  ← 从左侧选择功能\n", classes="hint"),
                    id="content-body",
                )
        yield Footer()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        self.query_one("#menu", ListView).focus()
        self._load_user_label()

    @work(thread=True)
    def _load_user_label(self) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            label = f"{client.stu_name} · {client.stu_id}"
        except Exception:  # noqa: BLE001
            label = "TJU"
        self.app.call_from_thread(self._set_panel_title, label)

    def _set_panel_title(self, label: str) -> None:
        self.query_one("#content-panel").border_title = label

    # ------------------------------------------------------------------
    # Navigation actions
    # ------------------------------------------------------------------

    def action_toggle_panel(self) -> None:
        menu = self.query_one("#menu", ListView)
        if menu.has_focus:
            self.action_focus_content()
        else:
            self.action_focus_menu()

    def action_focus_menu(self) -> None:
        self.query_one("#menu", ListView).focus()

    def action_focus_content(self) -> None:
        body = self.query_one("#content-body", VerticalScroll)
        # Focus the first focusable child (DataTable / Input) if present,
        # otherwise the scroll container itself.
        for child in body.query("DataTable, Input"):
            child.focus()
            return
        body.focus()

    def action_refresh(self) -> None:
        if self._current_action and self._current_action not in {
            "settings",
            "logout",
        }:
            self._run_action(self._current_action)

    # ------------------------------------------------------------------
    # Sidebar selection
    # ------------------------------------------------------------------

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        action = (event.item.id or "").removeprefix("item-")
        self._run_action(action)

    def _run_action(self, action: str) -> None:
        self._current_action = action
        self._request_id += 1  # invalidate any in-flight fetch
        rid = self._request_id

        if action == "settings":
            self.run_worker(self._show_settings, group="ui", exclusive=True)
            return
        if action == "logout":
            self._do_logout()
            return

        # Data actions: show loading, then fetch.
        self.run_worker(self._show_loading, group="ui", exclusive=True)

        if action == "profile":
            self._profile_worker(rid)
        elif action == "schedule":
            self._schedule_worker(rid, self._semester())
        elif action == "scores":
            self._scores_worker(rid)
        elif action == "exam":
            self._exam_worker(rid, self._semester())
        elif action == "exp_scores":
            self._exp_scores_worker(rid, self._semester())
        elif action == "courses":
            self._courses_worker(rid)
        elif action == "classrooms":
            self.run_worker(self._show_classroom_form, group="ui", exclusive=True)

    # ------------------------------------------------------------------
    # Content rendering primitives (async — awaits removal first)
    # ------------------------------------------------------------------

    async def _swap(self, *widgets) -> None:
        """Replace the content body with *widgets* (awaits removal first)."""
        body = self.query_one("#content-body", VerticalScroll)
        await body.remove_children()
        if widgets:
            await body.mount(*widgets)

    async def _show_loading(self) -> None:
        await self._swap(LoadingIndicator())

    async def _show_error(self, message: str) -> None:
        await self._swap(Static(f"  ⚠  {message}", classes="error-box"))

    async def _show_table(
        self, header: str, render_fn, data, param_bar: bool = False
    ) -> None:
        """Build the result widget on the main thread and mount it.

        ``render_fn`` is called here (not in the worker thread) because Textual
        ``DataTable`` construction requires the active-app context, which only
        exists on the event-loop thread.
        """
        widget = render_fn(data)
        children: list = []
        if param_bar:
            children.append(self._semester_bar())
        children.append(Static(header, classes="result-header"))
        children.append(widget)
        await self._swap(*children)
        # Focus the table so j/k scrolls immediately.
        try:
            widget.focus()
        except Exception:  # noqa: BLE001
            pass

    # ------------------------------------------------------------------
    # Param widgets
    # ------------------------------------------------------------------

    def _semester_bar(self) -> Horizontal:
        return Horizontal(
            Static("学期", classes="param-label"),
            Input(value=self._semester(), id="param-semester", classes="param-input"),
            Static("Enter 刷新", classes="param-hint"),
            classes="param-bar",
        )

    # ------------------------------------------------------------------
    # Settings panel
    # ------------------------------------------------------------------

    async def _show_settings(self) -> None:
        prefs = cfg.get_preferences()
        form = Vertical(
            Static("默认学期（留空则用系统当前学期）", classes="form-label"),
            Input(
                value=prefs.get("default_semester", ""),
                placeholder="如 25262",
                id="set-default-semester",
                classes="param-input",
            ),
            Static("回车保存", classes="param-hint"),
            classes="form",
        )
        await self._swap(form)
        self.query_one("#set-default-semester", Input).focus()

    async def _show_classroom_form(self) -> None:
        form = Vertical(
            Static("日期（YYYY-MM-DD）", classes="form-label"),
            Input(placeholder="2025-10-08", id="cr-date", classes="param-input"),
            Static("校区（2 卫津路 / 3 北洋园，留空全部）", classes="form-label"),
            Input(value="3", id="cr-campus", classes="param-input"),
            Static("起始节次 / 结束节次（1–12）", classes="form-label"),
            Input(value="1", id="cr-begin", classes="param-input"),
            Input(value="12", id="cr-end", classes="param-input"),
            Static("回车查询", classes="param-hint"),
            classes="form",
        )
        await self._swap(form)
        self.query_one("#cr-date", Input).focus()

    # ------------------------------------------------------------------
    # Input submitted (semester refresh / settings / classroom search)
    # ------------------------------------------------------------------

    def on_input_submitted(self, event: Input.Submitted) -> None:
        wid = event.input.id
        if wid == "param-semester":
            sem = event.input.value.strip()
            self._request_id += 1
            rid = self._request_id
            self.run_worker(self._show_loading, group="ui", exclusive=True)
            action = self._current_action
            if action == "schedule":
                self._schedule_worker(rid, sem)
            elif action == "exam":
                self._exam_worker(rid, sem)
            elif action == "exp_scores":
                self._exp_scores_worker(rid, sem)
        elif wid == "set-default-semester":
            cfg.set_preference("default_semester", event.input.value.strip())
            self.notify("设置已保存", title="设置")
        elif wid in {"cr-date", "cr-campus", "cr-begin", "cr-end"}:
            self._submit_classroom()

    def _submit_classroom(self) -> None:
        date_begin = self._val("cr-date")
        if not date_begin:
            self.notify("请输入日期", title="空闲教室", severity="warning")
            return
        campus = self._val("cr-campus") or None
        begin = self._val("cr-begin") or "1"
        end = self._val("cr-end") or "12"
        self._request_id += 1
        rid = self._request_id
        self.run_worker(self._show_loading, group="ui", exclusive=True)
        self._classrooms_worker(rid, date_begin, campus, begin, end)

    def _val(self, wid: str) -> str:
        try:
            return self.query_one(f"#{wid}", Input).value.strip()
        except Exception:  # noqa: BLE001
            return ""

    # ------------------------------------------------------------------
    # API workers — fetch raw data on a thread, render on main thread
    # ------------------------------------------------------------------

    def _client(self) -> Client:
        return self.app.client  # type: ignore[attr-defined,return-value]

    def _fail(self, rid: int, exc: Exception) -> None:
        if rid != self._request_id:
            return  # a newer request superseded this one
        msg = str(exc) if isinstance(exc, (DataError, HtmlParseError)) else f"请求失败：{exc}"
        self.app.call_from_thread(self._show_error, msg)

    def _done(self, rid: int, header: str, render_fn, data, param_bar: bool = False) -> None:
        if rid != self._request_id:
            return  # a newer request superseded this one
        # render_fn is invoked on the main thread inside _show_table.
        self.app.call_from_thread(self._show_table, header, render_fn, data, param_bar)

    @work(thread=True)
    def _profile_worker(self, rid: int) -> None:
        try:
            from tju.models import Profile  # noqa: PLC0415
            data = Profile.Schema().dump(self._client().profile)
        except Exception as exc:  # noqa: BLE001
            self._fail(rid, exc)
            return
        self._done(rid, "个人信息", render_profile, data)

    @work(thread=True)
    def _schedule_worker(self, rid: int, semester: str) -> None:
        try:
            from tju.models.schedule import Course  # noqa: PLC0415
            rows = Course.Schema(many=True).dump(
                list(self._client().schedule(semester=semester))
            )
        except Exception as exc:  # noqa: BLE001
            self._fail(rid, exc)
            return
        self._done(rid, f"共 {len(rows)} 门课程 · 学期 {semester}",
                   render_schedule, rows, param_bar=True)

    @work(thread=True)
    def _scores_worker(self, rid: int) -> None:
        try:
            client = self._client()
            result = client.score()
            score_list = result.get("list", [])
            if client.stu_type == StuType.GRADUATE:
                from tju.models.score import GSScore  # noqa: PLC0415
                rows = GSScore.Schema(many=True).dump(list(score_list))
                render_fn = render_gs_scores
            else:
                from tju.models.score import UGScore  # noqa: PLC0415
                rows = UGScore.Schema(many=True).dump(list(score_list))
                render_fn = render_ug_scores
        except Exception as exc:  # noqa: BLE001
            self._fail(rid, exc)
            return
        self._done(rid, f"共 {len(rows)} 条成绩记录", render_fn, rows)

    @work(thread=True)
    def _exam_worker(self, rid: int, semester: str) -> None:
        try:
            from tju.models.exam import Exam  # noqa: PLC0415
            rows = Exam.Schema(many=True).dump(
                list(self._client().exam(semester=semester))
            )
        except Exception as exc:  # noqa: BLE001
            self._fail(rid, exc)
            return
        self._done(rid, f"共 {len(rows)} 场考试 · 学期 {semester}",
                   render_exam, rows, param_bar=True)

    @work(thread=True)
    def _exp_scores_worker(self, rid: int, semester: str) -> None:
        try:
            from tju.models.score import ExpScore  # noqa: PLC0415
            rows = ExpScore.Schema(many=True).dump(
                list(self._client().exp_score(semester=semester))
            )
        except Exception as exc:  # noqa: BLE001
            self._fail(rid, exc)
            return
        self._done(rid, f"共 {len(rows)} 条实验成绩 · 学期 {semester}",
                   render_exp_scores, rows, param_bar=True)

    @work(thread=True)
    def _courses_worker(self, rid: int) -> None:
        try:
            from tju.models.course import LibCourse  # noqa: PLC0415
            result = self._client().query_courses()
            # query_courses returns a paged dict: {list, page_no, page_size, total}
            course_list = result.get("list", []) if isinstance(result, dict) else list(result)
            total = result.get("total", len(course_list)) if isinstance(result, dict) else len(course_list)
            rows = LibCourse.Schema(many=True).dump(list(course_list))
        except Exception as exc:  # noqa: BLE001
            self._fail(rid, exc)
            return
        self._done(rid, f"本页 {len(rows)} 门 · 共 {total} 门课程", render_courses, rows)

    @work(thread=True)
    def _classrooms_worker(
        self, rid: int, date_begin: str, campus_id: str | None,
        time_begin: str, time_end: str,
    ) -> None:
        try:
            from tju.models.classroom import FreeClassroom  # noqa: PLC0415
            rooms = self._client().free_classrooms(
                date_begin=date_begin,
                campus_id=campus_id,
                time_begin=time_begin,
                time_end=time_end,
            )
            rows = FreeClassroom.Schema(many=True).dump(list(rooms))
        except Exception as exc:  # noqa: BLE001
            self._fail(rid, exc)
            return
        self._done(rid, f"共 {len(rows)} 间空闲教室 · {date_begin}",
                   render_classrooms, rows)

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def _do_logout(self) -> None:
        cfg.clear_credentials()
        try:
            self._client()._session.logout()
        except Exception:  # noqa: BLE001
            pass
        self.app.client = None  # type: ignore[attr-defined]
        from .login import LoginScreen  # noqa: PLC0415

        self.app.switch_screen(LoginScreen())

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _semester(self) -> str:
        pref = cfg.get_preferences().get("default_semester", "")
        if pref:
            return pref
        try:
            return self._client().semester
        except Exception:  # noqa: BLE001
            return ""
