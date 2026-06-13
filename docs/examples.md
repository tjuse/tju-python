# Examples

All example scripts live in the `examples/` directory and write their output
to `examples/output/` (gitignored — real data never enters version control).

## Fetch personal timetable

Downloads and saves the current-semester personal course schedule.

**Run:**

```sh
uv run --env-file .env python examples/fetch_schedule.py
```

**What it does:**

1. Logs in with `TJU_USER` / `TJU_PASS`
2. Detects the current semester automatically
3. Calls `client.schedule(semester=semester)`
4. Prints a human-readable course list (name, credits, campus, class slots)
5. Serialises the full schedule with `Course.Schema(many=True).dump(...)` and
   writes it to `examples/output/schedule_<semester>.json`

**Sample output:**

```
============================================================
  学生: 张三  (1234567890)
  类型: GRADUATE
  学期: 25262
============================================================

共 3 门课程:

  [ 1] 随机过程基础  (2.0 学分)
       课号: S131GA04  班级: 05749
       校区: 北洋园校区  周次: 1-8
       上课: 周一 第 3~4 节  44楼A区211  [王勇]
       上课: 周三 第 1~2 节  44楼A区211  [王勇]
```

## Fetch full course library (UG + GS)

Downloads the entire public course catalogue — both undergraduate and graduate
libraries — and merges them into one file.

**Run:**

```sh
uv run --env-file .env python examples/fetch_all_courses.py
```

**What it does:**

1. Logs in and detects the current semester
2. Queries the undergraduate library (`project_id=1`) page by page (1000 courses/page)
3. Queries the graduate library (`project_id=22`) page by page
4. Tags each record with `student_type: "undergraduate" | "graduate"`
5. Serialises all records with `LibCourse.Schema(many=True).dump(...)` and writes
   `examples/output/courses_<semester>.json`

**Distinguishing UG vs. GS courses:**

| Signal | Undergraduate | Graduate |
|---|---|---|
| `student_type` field (injected) | `"undergraduate"` | `"graduate"` |
| `course_id` prefix | Numeric (`2xxxxxx`) | `S…` or `B…` |
| `selected` / `limit` fields | Populated | `null` (12-col format) |

**Sample output:**

```
正在爬取学期 25262 的本研全校课程 (每页 1000 条):

  [本科] 第 1 页  (1000/3580)
  ...
  [研究生] 第 2 页  (1571/1571)

  本科课程: 3580 门
  研究生课程: 1571 门
  合计: 5151 门
```
