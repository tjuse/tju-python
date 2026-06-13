"""Model for the student personal-information (profile) page."""

from datetime import date
from typing import Annotated, Optional

from marshmallow import EXCLUDE
from marshmallow_dataclass import dataclass

from tju.fields import ChineseBool, ChineseGender, ChineseStuType, DatetimeField
from tju.schema import LoadDumpSchema, mfield

from .base import Result
from .common import Gender, StuType


# fmt: off
@dataclass(frozen=True, base_schema=LoadDumpSchema)
class Profile(Result):
    """Complete student record scraped from the EAMS profile page.  Contains
    identity, enrolment, contact and supervisory information."""

    stu_id: Optional[str] = mfield(default=None, data_key="学号")
    stu_name: Optional[str] = mfield(default=None, data_key="姓名")
    stu_name_en: Optional[str] = mfield(default=None, data_key="英文名")
    gender: Annotated[Optional[Gender], ChineseGender] = mfield(default=None, data_key="性别")
    grade: Optional[str] = mfield(default=None, data_key="所在年级")
    edu_system: Optional[str] = mfield(default=None, data_key="学制")
    project: Optional[str] = mfield(default=None, data_key="项目")
    edu_level: Optional[str] = mfield(default=None, data_key="学历层次")
    stu_type: Annotated[Optional[StuType], ChineseStuType] = mfield(default=None, data_key="学生类别")
    faculty: Optional[str] = mfield(default=None, data_key="院系")
    major: Optional[str] = mfield(default=None, data_key="专业")
    direction: Optional[str] = mfield(default=None, data_key="方向")
    enrollment_date: Annotated[Optional[date], DatetimeField] = mfield(default=None, data_key="入学日期")
    graduation_date: Annotated[Optional[date], DatetimeField] = mfield(default=None, data_key="预毕业时间")
    admin_faculty: Optional[str] = mfield(default=None, data_key="行政管理院系")
    study_form: Optional[str] = mfield(default=None, data_key="学习形式")
    is_enrolled: Annotated[Optional[bool], ChineseBool] = mfield(default=None, data_key="是否在籍")
    is_on_campus: Annotated[Optional[bool], ChineseBool] = mfield(default=None, data_key="是否在校")
    campus: Optional[str] = mfield(default=None, data_key="所属校区")
    admin_class: Optional[str] = mfield(default=None, data_key="行政班")
    training_type: Optional[str] = mfield(default=None, data_key="培养类型")
    stu_tag: Optional[str] = mfield(default=None, data_key="学生标签")
    is_eth_class: Annotated[Optional[bool], ChineseBool] = mfield(default=None, data_key="是否民族班")
    effective_date: Annotated[Optional[date], DatetimeField] = mfield(default=None, data_key="学籍生效日期")
    has_enrolled: Annotated[Optional[bool], ChineseBool] = mfield(default=None, data_key="是否有学籍")
    training_plan: Optional[str] = mfield(default=None, data_key="培养方案")
    stu_category: Optional[str] = mfield(default=None, data_key="学生分类")
    cooperative_unit: Optional[str] = mfield(default=None, data_key="联合办学单位")
    original_class: Optional[str] = mfield(default=None, data_key="原班级")
    teaching_class: Optional[str] = mfield(default=None, data_key="教学班")
    remark: Optional[str] = mfield(default=None, data_key="备注")
    supervisor: Optional[str] = mfield(default=None, data_key="导师")
    co_supervisor: Optional[str] = mfield(default=None, data_key="合作导师")
    total_tuition: Optional[str] = mfield(default=None, data_key="总学费")
    scholarship_supervisor: Optional[str] = mfield(default=None, data_key="助学金导师")
    degree_category: Optional[str] = mfield(default=None, data_key="学位类别")
    stu_status: Optional[str] = mfield(default=None, data_key="学籍状态")
    cooperative_unit: Optional[str] = mfield(default=None, data_key="合作单位")
    orientation_unit: Optional[str] = mfield(default=None, data_key="定向单位")
    stu_on_campus_category: Optional[str] = mfield(default=None, data_key="在校生类别")
    is_off_campus: Annotated[Optional[bool], ChineseBool] = mfield(default=None, data_key="是否校外生")
    training_mode: Optional[str] = mfield(default=None, data_key="培养模式")
    email: Optional[str] = mfield(default=None, data_key="电子邮件")
    phone: Optional[str] = mfield(default=None, data_key="联系电话")
    mobile: Optional[str] = mfield(default=None, data_key="移动电话")
    address: Optional[str] = mfield(default=None, data_key="联系地址")
    home_phone: Optional[str] = mfield(default=None, data_key="家庭电话")
    home_address: Optional[str] = mfield(default=None, data_key="家庭地址")
    home_address_zip: Optional[str] = mfield(default=None, data_key="家庭地址邮编")

    class Meta:
        unknown = EXCLUDE
