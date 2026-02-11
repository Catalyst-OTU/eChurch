from crud.base import CRUDBase
from domains.echurch.models.attendance import FollowUpTemplate, MemberAttendance
from domains.echurch.schemas.attendance import AttendanceEntryCreate, FollowUpTemplateUpdate


class CRUDMemberAttendance(CRUDBase[MemberAttendance, AttendanceEntryCreate, AttendanceEntryCreate]):
    pass


class CRUDFollowUpTemplate(CRUDBase[FollowUpTemplate, FollowUpTemplateUpdate, FollowUpTemplateUpdate]):
    pass


member_attendance_repo = CRUDMemberAttendance(MemberAttendance)
follow_up_template_repo = CRUDFollowUpTemplate(FollowUpTemplate)

