<p align="center"><b>TJU</b> <sup><samp>The Python TJU client</samp></sup></p>

[![PyPI version](https://img.shields.io/pypi/v/tju.svg)](https://pypi.org/project/tju/)

[English](README.md) | 简体中文

> **开发中。** API 可用，但尚未稳定。

`tju` 是一个 Python 库，用于登录天津大学 SSO 和 EAMS 学务系统并返回结构化的学业数据。它内置了 CAS 认证、验证码识别（通过 `ddddocr`）和 HTML 解析，你只需调用方法即可获得类型化的数据对象。

> **网络要求：** 所有实时 API 调用均需连接天津大学校园网或 VPN（`sso.tju.edu.cn` / `classes.tju.edu.cn`）。

## 功能

| 功能 | 客户端方法 |
|---|---|
| 学生个人信息 | `client.profile` |
| 个人课表 | `client.schedule(semester)` |
| 公共课程库 | `client.query_courses(semester)` |
| 课程详情 | `client.query_course_info(lession_id)` |
| 课程大纲 | `client.query_syllabus(lession_id)` |
| 考试安排 | `client.exam(semester)` |
| 成绩（本科生 + 研究生） | `client.score()` |
| 实验成绩 | `client.exp_score(semester)` |
| 空教室查询 | `client.free_classrooms(date_begin, ...)` |

## 安装

```sh
pip install tju
```

从源码安装（推荐用于开发）：

```sh
git clone https://github.com/superpung/tju-python.git
cd tju-python
uv sync       # 将所有依赖安装到 .venv
```

## 快速开始

将凭据设置为环境变量（或写入 `.env` 文件）：

```sh
export TJU_USER=your_student_id
export TJU_PASS=your_password
```

```python
from tju.client import create_client

client = create_client()   # 从环境变量读取 TJU_USER / TJU_PASS
print(client.profile)
print(client.schedule(semester="24251"))
```

**可运行示例：**

```sh
# 个人课表 — 打印你的课程并保存 JSON
uv run --env-file .env python examples/fetch_schedule.py

# 全部课程库 — 爬取所有分页并保存 JSON
uv run --env-file .env python examples/fetch_all_courses.py
```

两个脚本均将输出写入 `examples/output/`（已 gitignore）。

## 使用方法

```python
from tju import Session
from tju.client import Client

session = Session()                              # 或: Session(username=..., password=...)
client  = Client(session=session)

# 身份信息
client.stu_id        # 学号字符串
client.stu_name      # 姓名字符串
client.stu_type      # StuType.UNDERGRADUATE | StuType.GRADUATE
client.has_minor     # bool，是否有辅修
client.semester      # 当前学期代码，例如 "24252"

# 数据查询
client.profile
client.schedule(semester="24251")
client.query_courses(semester="24251")
client.query_course_info(lession_id="387248")
client.query_syllabus(lession_id="387248")
client.exam(semester="24251")
client.score()
client.exp_score(semester="20211")
client.free_classrooms(date_begin="2025-10-08", campus_id=3)
```

学期代码遵循 EAMS 规范，例如 `"24251"` = 2024–2025 学年第一学期，
`"24252"` = 2024–2025 学年第二学期。完整的 `SEMESTER` 映射表见 `src/tju/consts.py`。

## 开发

```sh
uv sync          # 安装运行时及开发依赖
uv run pytest    # 运行离线测试套件（30 个测试，无需网络）
```

架构细节与贡献指南请参见 [AGENTS.md](AGENTS.md)。

## 许可证

[GPLv3 License](LICENSE) © 2023-PRESENT Super Lee
