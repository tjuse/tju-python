"""Main application screen — sidebar navigation + content panel."""

from __future__ import annotations

from typing import Any

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    DataTable,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Markdown,
    Static,
)

from tju.client import Client
from tju.exceptions import DataError, HtmlParseError
from tju.models import StuType

from .. import config as cfg
from ..render import (
    render_classrooms,
    render_courses,
    render_exam,
    render_exp_scores,
    render_gs_scores,
    render_markdown,
    render_profile,
    render_schedule,
    render_ug_scores,
)

# ---------------------------------------------------------------------------
# Sidebar menu items
# ---------------------------------------------------------------------------

_ACTIONS = [
    ("profile",     "👤  个人信息"),
    ("schedule",    "📅  课表"),
    ("courses",     "📚  课程库"),
    ("exam",        "📝  考试安排"),
    ("scores",      "🏆  成绩"),
    ("exp_scores",  "🔬  实验成绩"),
    ("classrooms",  "🏫  空闲教室"),
    ("settings",    "⚙️   设置"),
    ("logout",      "🚪  退出登录"),
]


class MainScreen(Screen):
    """Two-pane main screen.

    Left:  sidebar ``ListView`` of available actions.
    Right: content panel that shows parameter forms and data tables.
    """

    # Displayed name of the current action
    _current_action: str = ""

    def compose(self) -> ComposeResult:
        # Top bar
        with Horizontal(id="topbar"):
            yield Static("TJU", id="topbar-title")
            yield Static("", id="topbar-user")

        # Body: sidebar + content
        with Horizontal(id="body"):
            with Vertical(id="sidebar"):
                yield ListView(
                    *[ListItem(Static(label), id=f"item-{action_id}")
                      for action_id, label in _ACTIONS],
                    id="sidebar-list",
                )
            with Vertical(id="content"):
                yield Static("← 从左侧菜单选择功能", id="content-placeholder")

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def on_mount(self) -> None:
        self._load_user_label()

    @work(thread=True)
    def _load_user_label(self) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            label = f"{client.stu_name}（{client.stu_id}）"
        except Exception:  # noqa: BLE001
            label = ""
        self.app.call_from_thread(self._set_user_label, label)

    def _set_user_label(self, label: str) -> None:
        self.query_one("#topbar-user", Static).update(label)

    # ------------------------------------------------------------------
    # Sidebar selection
    # ------------------------------------------------------------------

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        item_id: str = event.item.id or ""
        action = item_id.removeprefix("item-")
        self._current_action = action
        self._show_panel(action)

    def _show_panel(self, action: str) -> None:
        """Clear the content area and mount the panel for *action*."""
        content = self.query_one("#content")
        for child in list(content.children):
            child.remove()

        if action == "profile":
            self._panel_profile(content)
        elif action == "schedule":
            self._panel_form(content, "课表", "学期（如 24251）", "semester",
                             default=self._default_semester())
        elif action == "courses":
            self._panel_courses(content)
        elif action == "exam":
            self._panel_form(content, "考试安排", "学期（如 24251）", "semester",
                             default=self._default_semester())
        elif action == "exp_scores":
            self._panel_form(content, "实验成绩", "学期（如 24251）", "semester",
                             default=self._default_semester())
        elif action == "scores":
            self._panel_scores(content)
        elif action == "classrooms":
            self._panel_classrooms(content)
        elif action == "settings":
            self._panel_settings(content)
        elif action == "logout":
            self._do_logout()

    # ------------------------------------------------------------------
    # Panel builders — mount widgets into *container*
    # ------------------------------------------------------------------

    def _panel_profile(self, container: Widget) -> None:
        container.mount(Static("个人信息", id="content-title"))
        loading = LoadingIndicator(id="loading")
        container.mount(loading)
        container.mount(Static("", id="error-msg"))
        container.mount(Vertical(id="result-area"))
        self._fetch_profile()

    def _panel_form(
        self,
        container: Widget,
        title: str,
        label: str,
        field: str,
        default: str = "",
    ) -> None:
        container.mount(Static(title, id="content-title"))
        form = Vertical(id="param-form")
        container.mount(form)
        form.mount(Label(label))
        form.mount(Input(value=default, id=f"input-{field}"))
        form.mount(Button("查 询", variant="primary", id="btn-fetch"))
        loading = LoadingIndicator(id="loading")
        loading.display = False
        container.mount(loading)
        container.mount(Static("", id="error-msg"))
        container.mount(Vertical(id="result-area"))

    def _panel_courses(self, container: Widget) -> None:
        container.mount(Static("课程库", id="content-title"))
        form = Vertical(id="param-form")
        container.mount(form)
        form.mount(Label("查询当前学期公开课程库（本科生/研究生均可）"))
        form.mount(Button("查 询", variant="primary", id="btn-fetch"))
        loading = LoadingIndicator(id="loading")
        loading.display = False
        container.mount(loading)
        container.mount(Static("", id="error-msg"))
        container.mount(Vertical(id="result-area"))

    def _panel_scores(self, container: Widget) -> None:
        container.mount(Static("成绩", id="content-title"))
        form = Vertical(id="param-form")
        container.mount(form)
        form.mount(Label("查询全部历史成绩"))
        form.mount(Button("查 询", variant="primary", id="btn-fetch"))
        loading = LoadingIndicator(id="loading")
        loading.display = False
        container.mount(loading)
        container.mount(Static("", id="error-msg"))
        container.mount(Vertical(id="result-area"))

    def _panel_classrooms(self, container: Widget) -> None:
        container.mount(Static("空闲教室", id="content-title"))
        form = Vertical(id="param-form")
        container.mount(form)
        form.mount(Label("日期（YYYY-MM-DD）"))
        form.mount(Input(placeholder="2025-10-08", id="input-date_begin"))
        form.mount(Label("校区 ID（2=卫津路 / 3=北洋园，留空不过滤）"))
        form.mount(Input(placeholder="3", id="input-campus_id"))
        form.mount(Label("开始节次（1–12，默认 1）"))
        form.mount(Input(value="1", id="input-time_begin"))
        form.mount(Label("结束节次（1–12，默认 12）"))
        form.mount(Input(value="12", id="input-time_end"))
        form.mount(Button("查 询", variant="primary", id="btn-fetch"))
        loading = LoadingIndicator(id="loading")
        loading.display = False
        container.mount(loading)
        container.mount(Static("", id="error-msg"))
        container.mount(Vertical(id="result-area"))

    def _panel_settings(self, container: Widget) -> None:
        container.mount(Static("设置", id="content-title"))
        prefs = cfg.get_preferences()
        form = Vertical(id="param-form")
        container.mount(form)
        form.mount(Label("默认学期（留空使用系统当前学期）"))
        form.mount(Input(
            value=prefs.get("default_semester", ""),
            id="input-default_semester",
        ))
        form.mount(Button("保 存", variant="primary", id="btn-save-settings"))
        container.mount(Static("", id="error-msg"))

    # ------------------------------------------------------------------
    # Button events
    # ------------------------------------------------------------------

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-fetch":
            self._dispatch_fetch()
        elif btn_id == "btn-save-settings":
            self._save_settings()

    def _dispatch_fetch(self) -> None:
        action = self._current_action
        if action == "profile":
            self._fetch_profile()
        elif action == "schedule":
            semester = self._input_value("input-semester")
            if not semester:
                self._show_error("请输入学期")
                return
            self._fetch_schedule(semester)
        elif action == "courses":
            self._fetch_courses()
        elif action == "exam":
            semester = self._input_value("input-semester")
            if not semester:
                self._show_error("请输入学期")
                return
            self._fetch_exam(semester)
        elif action == "scores":
            self._fetch_scores()
        elif action == "exp_scores":
            semester = self._input_value("input-semester")
            if not semester:
                self._show_error("请输入学期")
                return
            self._fetch_exp_scores(semester)
        elif action == "classrooms":
            date_begin = self._input_value("input-date_begin")
            if not date_begin:
                self._show_error("请输入日期")
                return
            campus_id = self._input_value("input-campus_id") or None
            time_begin = self._input_value("input-time_begin") or "1"
            time_end = self._input_value("input-time_end") or "12"
            self._fetch_classrooms(date_begin, campus_id, time_begin, time_end)

    # ------------------------------------------------------------------
    # API workers
    #
    # Pattern: worker thread fetches raw data (dicts/lists), then calls
    # call_from_thread with a *data* callback that creates the widget on
    # the main thread.  DataTable methods must only be called on the main
    # event loop thread.
    # ------------------------------------------------------------------

    def _fetch_profile(self) -> None:
        self._set_loading(True)
        self._profile_worker()

    @work(thread=True)
    def _profile_worker(self) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            from tju.models import Profile  # noqa: PLC0415
            profile = client.profile
            data: dict[str, Any] = Profile.Schema().dump(profile)
        except (DataError, HtmlParseError) as exc:
            self.app.call_from_thread(self._show_error, str(exc))
            self.app.call_from_thread(self._set_loading, False)
            return
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._show_error, f"请求失败: {exc}")
            self.app.call_from_thread(self._set_loading, False)
            return
        self.app.call_from_thread(self._on_profile_data, data)

    def _on_profile_data(self, data: dict[str, Any]) -> None:
        self._show_widget(render_profile(data))
        self._set_loading(False)

    # ---- Schedule ----

    def _fetch_schedule(self, semester: str) -> None:
        self._set_loading(True)
        self._schedule_worker(semester)

    @work(thread=True)
    def _schedule_worker(self, semester: str) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            from tju.models.schedule import Course  # noqa: PLC0415
            schedule = client.schedule(semester=semester)
            rows: list[dict[str, Any]] = Course.Schema(many=True).dump(list(schedule))
        except (DataError, HtmlParseError) as exc:
            self.app.call_from_thread(self._show_error, str(exc))
            self.app.call_from_thread(self._set_loading, False)
            return
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._show_error, f"请求失败: {exc}")
            self.app.call_from_thread(self._set_loading, False)
            return
        label = f"共 {len(rows)} 门课程 — 学期 {semester}"
        self.app.call_from_thread(self._on_tabular_data, rows, "schedule", label)

    # ---- Courses ----

    def _fetch_courses(self) -> None:
        self._set_loading(True)
        self._courses_worker()

    @work(thread=True)
    def _courses_worker(self) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            from tju.models.course import LibCourse  # noqa: PLC0415
            courses = client.query_courses()
            rows: list[dict[str, Any]] = LibCourse.Schema(many=True).dump(list(courses))
        except (DataError, HtmlParseError) as exc:
            self.app.call_from_thread(self._show_error, str(exc))
            self.app.call_from_thread(self._set_loading, False)
            return
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._show_error, f"请求失败: {exc}")
            self.app.call_from_thread(self._set_loading, False)
            return
        label = f"共 {len(rows)} 门课程"
        self.app.call_from_thread(self._on_tabular_data, rows, "courses", label)

    # ---- Exam ----

    def _fetch_exam(self, semester: str) -> None:
        self._set_loading(True)
        self._exam_worker(semester)

    @work(thread=True)
    def _exam_worker(self, semester: str) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            from tju.models.exam import Exam  # noqa: PLC0415
            exams = client.exam(semester=semester)
            rows: list[dict[str, Any]] = Exam.Schema(many=True).dump(list(exams))
        except (DataError, HtmlParseError) as exc:
            self.app.call_from_thread(self._show_error, str(exc))
            self.app.call_from_thread(self._set_loading, False)
            return
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._show_error, f"请求失败: {exc}")
            self.app.call_from_thread(self._set_loading, False)
            return
        label = f"共 {len(rows)} 场考试 — 学期 {semester}"
        self.app.call_from_thread(self._on_tabular_data, rows, "exam", label)

    # ---- Scores ----

    def _fetch_scores(self) -> None:
        self._set_loading(True)
        self._scores_worker()

    @work(thread=True)
    def _scores_worker(self) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            result = client.score()
            is_gs = client.stu_type == StuType.GRADUATE
            score_list = result.get("list", [])
            if is_gs:
                from tju.models.score import GSScore  # noqa: PLC0415
                rows: list[dict[str, Any]] = GSScore.Schema(many=True).dump(list(score_list))
                kind = "gs_scores"
            else:
                from tju.models.score import UGScore  # noqa: PLC0415
                rows = UGScore.Schema(many=True).dump(list(score_list))
                kind = "ug_scores"
        except (DataError, HtmlParseError) as exc:
            self.app.call_from_thread(self._show_error, str(exc))
            self.app.call_from_thread(self._set_loading, False)
            return
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._show_error, f"请求失败: {exc}")
            self.app.call_from_thread(self._set_loading, False)
            return
        label = f"共 {len(rows)} 条成绩记录"
        self.app.call_from_thread(self._on_tabular_data, rows, kind, label)

    # ---- Exp scores ----

    def _fetch_exp_scores(self, semester: str) -> None:
        self._set_loading(True)
        self._exp_scores_worker(semester)

    @work(thread=True)
    def _exp_scores_worker(self, semester: str) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            from tju.models.score import ExpScore  # noqa: PLC0415
            exp = client.exp_score(semester=semester)
            rows: list[dict[str, Any]] = ExpScore.Schema(many=True).dump(list(exp))
        except (DataError, HtmlParseError) as exc:
            self.app.call_from_thread(self._show_error, str(exc))
            self.app.call_from_thread(self._set_loading, False)
            return
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._show_error, f"请求失败: {exc}")
            self.app.call_from_thread(self._set_loading, False)
            return
        label = f"共 {len(rows)} 条实验成绩 — 学期 {semester}"
        self.app.call_from_thread(self._on_tabular_data, rows, "exp_scores", label)

    # ---- Classrooms ----

    def _fetch_classrooms(
        self,
        date_begin: str,
        campus_id: str | None,
        time_begin: str,
        time_end: str,
    ) -> None:
        self._set_loading(True)
        self._classrooms_worker(date_begin, campus_id, time_begin, time_end)

    @work(thread=True)
    def _classrooms_worker(
        self,
        date_begin: str,
        campus_id: str | None,
        time_begin: str,
        time_end: str,
    ) -> None:
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            from tju.models.classroom import FreeClassroom  # noqa: PLC0415
            classrooms = client.free_classrooms(
                date_begin=date_begin,
                campus_id=campus_id,
                time_begin=time_begin,
                time_end=time_end,
            )
            rows: list[dict[str, Any]] = FreeClassroom.Schema(many=True).dump(
                list(classrooms)
            )
        except (DataError, HtmlParseError) as exc:
            self.app.call_from_thread(self._show_error, str(exc))
            self.app.call_from_thread(self._set_loading, False)
            return
        except Exception as exc:  # noqa: BLE001
            self.app.call_from_thread(self._show_error, f"请求失败: {exc}")
            self.app.call_from_thread(self._set_loading, False)
            return
        label = f"共 {len(rows)} 间空闲教室 — {date_begin}"
        self.app.call_from_thread(self._on_tabular_data, rows, "classrooms", label)

    # ------------------------------------------------------------------
    # Main-thread data callbacks (widget creation happens here)
    # ------------------------------------------------------------------

    def _on_tabular_data(
        self, rows: list[dict[str, Any]], kind: str, label: str
    ) -> None:
        """Create and mount a result widget from serialised *rows* (main thread)."""
        render_map = {
            "schedule":   render_schedule,
            "courses":    render_courses,
            "exam":       render_exam,
            "ug_scores":  render_ug_scores,
            "gs_scores":  render_gs_scores,
            "exp_scores": render_exp_scores,
            "classrooms": render_classrooms,
        }
        renderer = render_map.get(kind)
        if renderer is None:
            return
        widget = renderer(rows)
        self._show_widget(widget, label)
        self._set_loading(False)

    # ------------------------------------------------------------------
    # Settings save
    # ------------------------------------------------------------------

    def _save_settings(self) -> None:
        semester = self._input_value("input-default_semester")
        cfg.set_preference("default_semester", semester)
        self.notify("设置已保存", title="设置")

    # ------------------------------------------------------------------
    # Logout
    # ------------------------------------------------------------------

    def _do_logout(self) -> None:
        cfg.clear_credentials()
        client: Client = self.app.client  # type: ignore[attr-defined]
        try:
            client._session.logout()
        except Exception:  # noqa: BLE001
            pass
        self.app.client = None  # type: ignore[attr-defined]
        from .login import LoginScreen  # noqa: PLC0415

        self.app.switch_screen(LoginScreen())

    # ------------------------------------------------------------------
    # UI helpers
    # ------------------------------------------------------------------

    def _input_value(self, widget_id: str) -> str:
        try:
            return self.query_one(f"#{widget_id}", Input).value.strip()
        except Exception:  # noqa: BLE001
            return ""

    def _set_loading(self, loading: bool) -> None:
        try:
            widget = self.query_one("#loading", LoadingIndicator)
            widget.display = loading
        except Exception:  # noqa: BLE001
            pass
        try:
            btn = self.query_one("#btn-fetch", Button)
            btn.disabled = loading
        except Exception:  # noqa: BLE001
            pass

    def _show_error(self, message: str) -> None:
        try:
            w = self.query_one("#error-msg", Static)
            w.update(f"⚠ {message}")
            w.add_class("visible")
        except Exception:  # noqa: BLE001
            self.notify(message, title="错误", severity="error")

    def _show_widget(self, widget: Widget, subtitle: str = "") -> None:
        """Mount *widget* into the result area, replacing previous results."""
        try:
            area = self.query_one("#result-area")
        except Exception:  # noqa: BLE001
            return
        for child in list(area.children):
            child.remove()
        try:
            self.query_one("#error-msg", Static).remove_class("visible")
        except Exception:  # noqa: BLE001
            pass
        if subtitle:
            area.mount(Static(subtitle))
        area.mount(widget)

    def _default_semester(self) -> str:
        return cfg.get_preferences().get("default_semester", "")
