from datetime import datetime
from typing import Optional

from marshmallow_dataclass import dataclass

from .common import Gender, StuType


@dataclass(frozen=True)
class Profile:
    stu_id: Optional[str]
    stu_name: Optional[str]
    stu_name_en: Optional[str]
    gender: Gender
    grade: Optional[str]
    edu_system: Optional[str]
    project: Optional[str]
    edu_level: Optional[str]
    stu_type: StuType
    faculty: Optional[str]
    major: Optional[str]
    direction: Optional[str]
    enrollment_date: datetime
    graduation_date: datetime
    admin_faculty: Optional[str]
    study_form: Optional[str]
    is_enrolled: Optional[str]
    is_on_campus: Optional[str]
    campus: Optional[str]
    admin_class: Optional[str]
    training_type: Optional[str]
    stu_tag: Optional[str]
    is_eth_class: Optional[str]
    effective_date: datetime
    is_enrolled: Optional[str]
    training_plan: Optional[str]
    stu_category: Optional[str]
    cooperative_unit: Optional[str]
    original_class: Optional[str]
    teaching_class: Optional[str]
    remark: Optional[str]
    supervisor: Optional[str]
    co_supervisor: Optional[str]
    total_tuition: Optional[str]
    scholarship_supervisor: Optional[str]
    degree_category: Optional[str]
    stu_status: Optional[str]
    cooperative_unit: Optional[str]
    orientation_unit: Optional[str]
    stu_on_campus_category: Optional[str]
    is_off_campus: Optional[str]
    training_mode: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    mobile: Optional[str]
    address: Optional[str]
    home_phone: Optional[str]
    home_address: Optional[str]
    home_address_zip: Optional[str]
