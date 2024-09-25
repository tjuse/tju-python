import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict

from tju.models import Gender, StuType


@dataclass(frozen=True)
class ProfileField:
    _key: str
    _raw_key: str
    _parse: Callable[[str], Any] = lambda x: x

    def parse(self, value):
        return self._parse(value)


def parse_profile(html) -> Dict[str, Any]:
    """
    parse personal profile
    """

    matches = re.findall(
        r'<td[ width="25%"]* class="title" style="width:18%">([^<]+)</td>\s*<td[^>]*>([^<]*)</td>',
        html,
    )
    result = {
        key.strip("：") if key.endswith("：") else key: value for key, value in matches
    }

    parsed_result = {
        field._key: field.parse(result.get(field._raw_key)) for field in profile_fields
    }

    return parsed_result


# fmt: off
profile_fields = [
    ProfileField("stu_id", "学号", str),
    ProfileField("stu_name", "姓名", str),
    ProfileField("stu_name_en", "英文名", str),
    ProfileField("gender", "性别", lambda x: Gender.MALE if x == "男" else Gender.FEMALE),
    ProfileField("grade", "所在年级", str),
    ProfileField("edu_system", "学制", str),
    ProfileField("project", "项目", str),
    ProfileField("edu_level", "学历层次", str),
    ProfileField("stu_type", "学生类别", lambda x: StuType.UNDERGRADUATE if x == "本科生" else StuType.GRADUATE),
    ProfileField("faculty", "院系", str),
    ProfileField("major", "专业", str),
    ProfileField("direction", "方向", str),
    ProfileField("enrollment_date", "入学日期", lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
    ProfileField("graduation_date", "预毕业时间", lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
    ProfileField("admin_faculty", "行政管理院系", str),
    ProfileField("study_form", "学习形式", str),
    ProfileField("is_enrolled", "是否在籍", lambda x: x == "是"),
    ProfileField("is_on_campus", "是否在校", lambda x: x == "是"),
    ProfileField("campus", "所属校区", str),
    ProfileField("admin_class", "行政班", str),
    ProfileField("training_type", "培养类型", str),
    ProfileField("stu_tag", "学生标签", str),
    ProfileField("is_eth_class", "是否民族班", lambda x: x == "是"),
    ProfileField("effective_date", "学籍生效日期", lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
    ProfileField("is_enrolled", "是否有学籍", lambda x: x == "是"),
    ProfileField("training_plan", "培养方案", str),
    ProfileField("stu_category", "学生分类", str),
    ProfileField("cooperative_unit", "联合办学单位", str),
    ProfileField("original_class", "原班级", str),
    ProfileField("teaching_class", "教学班", str),
    ProfileField("remark", "备注", str),
    ProfileField("supervisor", "导师", str),
    ProfileField("co_supervisor", "合作导师", str),
    ProfileField("total_tuition", "总学费", str),
    ProfileField("scholarship_supervisor", "助学金导师", str),
    ProfileField("degree_category", "学位类别", str),
    ProfileField("stu_status", "学籍状态", str),
    ProfileField("cooperative_unit", "合作单位", str),
    ProfileField("orientation_unit", "定向单位", str),
    ProfileField("stu_on_campus_category", "在校生类别", str),
    ProfileField("is_off_campus", "是否校外生", lambda x: x == "是"),
    ProfileField("training_mode", "培养模式", str),
    ProfileField("email", "电子邮件", str),
    ProfileField("phone", "联系电话", str),
    ProfileField("mobile", "移动电话", str),
    ProfileField("address", "联系地址", str),
    ProfileField("home_phone", "家庭电话", str),
    ProfileField("home_address", "家庭地址", str),
    ProfileField("home_address_zip", "家庭地址邮编", str),
]
