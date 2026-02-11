from crud.base import CRUDBase
from domains.echurch.models.group import Group, GroupAttendance, GroupMember
from domains.echurch.schemas.group import GroupAttendanceCreate, GroupAssignMemberRequest, GroupCreate, GroupUpdate


class CRUDGroup(CRUDBase[Group, GroupCreate, GroupUpdate]):
    pass


class CRUDGroupMember(CRUDBase[GroupMember, GroupAssignMemberRequest, GroupAssignMemberRequest]):
    pass


class CRUDGroupAttendance(CRUDBase[GroupAttendance, GroupAttendanceCreate, GroupAttendanceCreate]):
    pass


group_repo = CRUDGroup(Group)
group_member_repo = CRUDGroupMember(GroupMember)
group_attendance_repo = CRUDGroupAttendance(GroupAttendance)

