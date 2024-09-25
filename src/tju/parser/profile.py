import re
from datetime import datetime
from typing import Any, Dict

from tju.fields import Field
from tju.models import Gender, StuType


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
    Field("stu_id", "学号", str),
    Field("stu_name", "姓名", str),
    Field("stu_name_en", "英文名", str),
    Field("gender", "性别", lambda x: Gender.MALE if x == "男" else Gender.FEMALE),
    Field("grade", "所在年级", str),
    Field("edu_system", "学制", str),
    Field("project", "项目", str),
    Field("edu_level", "学历层次", str),
    Field("stu_type", "学生类别", lambda x: StuType.UNDERGRADUATE if x == "本科生" else StuType.GRADUATE),
    Field("faculty", "院系", str),
    Field("major", "专业", str),
    Field("direction", "方向", str),
    Field("enrollment_date", "入学日期", lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
    Field("graduation_date", "预毕业时间", lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
    Field("admin_faculty", "行政管理院系", str),
    Field("study_form", "学习形式", str),
    Field("is_enrolled", "是否在籍", lambda x: x == "是"),
    Field("is_on_campus", "是否在校", lambda x: x == "是"),
    Field("campus", "所属校区", str),
    Field("admin_class", "行政班", str),
    Field("training_type", "培养类型", str),
    Field("stu_tag", "学生标签", str),
    Field("is_eth_class", "是否民族班", lambda x: x == "是"),
    Field("effective_date", "学籍生效日期", lambda x: datetime.strptime(x, "%Y-%m-%d").date()),
    Field("is_enrolled", "是否有学籍", lambda x: x == "是"),
    Field("training_plan", "培养方案", str),
    Field("stu_category", "学生分类", str),
    Field("cooperative_unit", "联合办学单位", str),
    Field("original_class", "原班级", str),
    Field("teaching_class", "教学班", str),
    Field("remark", "备注", str),
    Field("supervisor", "导师", str),
    Field("co_supervisor", "合作导师", str),
    Field("total_tuition", "总学费", str),
    Field("scholarship_supervisor", "助学金导师", str),
    Field("degree_category", "学位类别", str),
    Field("stu_status", "学籍状态", str),
    Field("cooperative_unit", "合作单位", str),
    Field("orientation_unit", "定向单位", str),
    Field("stu_on_campus_category", "在校生类别", str),
    Field("is_off_campus", "是否校外生", lambda x: x == "是"),
    Field("training_mode", "培养模式", str),
    Field("email", "电子邮件", str),
    Field("phone", "联系电话", str),
    Field("mobile", "移动电话", str),
    Field("address", "联系地址", str),
    Field("home_phone", "家庭电话", str),
    Field("home_address", "家庭地址", str),
    Field("home_address_zip", "家庭地址邮编", str),
]
