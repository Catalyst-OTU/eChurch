from typing import List, Literal, Optional

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy.orm import Session, selectinload

from domains.echurch.models.group import Group, GroupAttendance, GroupMember
from domains.echurch.repositories.group import group_repo
from domains.echurch.repositories.member import member_repo
from domains.echurch.schemas.department import DepartmentBriefSchema
from domains.echurch.schemas.group import (
    GroupAssignMemberRequest,
    GroupAttendanceCreate,
    GroupAttendanceSchema,
    GroupCreate,
    GroupDetailSchema,
    GroupListItemSchema,
    GroupMemberItemSchema,
    GroupSchema,
    GroupUpdate,
)


class GroupService:
    def __init__(self):
        self.repo = group_repo

    def list_groups(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        order_by: Optional[str] = None,
        order_direction: Literal["asc", "desc"] = "asc",
    ) -> List[GroupListItemSchema]:
        query = (
            db.query(Group)
            .options(
                selectinload(Group.centre),
                selectinload(Group.group_members).selectinload(GroupMember.role_department),
            )
            .filter(Group.is_deleted.is_(False))
        )

        if search:
            query = query.filter(Group.name.ilike(f"%{search.strip()}%"))

        if order_by:
            try:
                col = getattr(Group, order_by)
            except AttributeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid order_by column: {order_by}"
                )
            query = query.order_by(col.desc() if order_direction == "desc" else col.asc())
        else:
            query = query.order_by(Group.created_date.desc())

        groups = query.offset(skip).limit(limit).all()
        items: List[GroupListItemSchema] = []
        for group in groups:
            active_members = [gm for gm in group.group_members if gm.is_active and not gm.is_deleted]
            roles = sorted({gm.role_department.name for gm in active_members if gm.role_department})
            item = GroupListItemSchema.model_validate(group, from_attributes=True)
            item.members_count = len(active_members)
            item.roles = roles
            items.append(item)
        return items

    def create_group(self, db: Session, *, data: GroupCreate) -> GroupSchema:
        return self.repo.create(db=db, data=data, unique_fields=["name"])

    def update_group(self, db: Session, *, id: UUID4, data: GroupUpdate) -> GroupSchema:
        group = self.repo.get_by_id(db=db, id=id)
        return self.repo.update(db=db, db_obj=group, data=data, unique_fields=["name"])

    def delete_group(self, db: Session, *, id: UUID4) -> None:
        self.repo.delete(db=db, id=id, soft=False)

    def get_group_detail(self, db: Session, *, id: UUID4) -> GroupDetailSchema:
        group = (
            db.query(Group)
            .options(
                selectinload(Group.centre),
                selectinload(Group.group_members).selectinload(GroupMember.member),
                selectinload(Group.group_members).selectinload(GroupMember.role_department),
            )
            .filter(Group.id == id)
            .one_or_none()
        )
        if not group:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Group not found")

        active_members = [gm for gm in group.group_members if gm.is_active and not gm.is_deleted]
        roles = sorted({gm.role_department.name for gm in active_members if gm.role_department})

        members: List[GroupMemberItemSchema] = []
        for gm in active_members:
            role_schema = (
                DepartmentBriefSchema.model_validate(gm.role_department, from_attributes=True)
                if gm.role_department
                else None
            )
            members.append(
                GroupMemberItemSchema(
                    member_id=gm.member_id,
                    member_name=gm.member.full_name if gm.member else "",
                    member_phone=gm.member.phone_number if gm.member else None,
                    role=role_schema,
                )
            )

        detail = GroupDetailSchema.model_validate(group, from_attributes=True)
        detail.members_count = len(active_members)
        detail.roles = roles
        detail.members = members
        return detail

    def assign_member(self, db: Session, *, data: GroupAssignMemberRequest) -> GroupMember:
        self.repo.get_by_id(db=db, id=data.group_id)
        member_repo.get_by_id(db=db, id=data.member_id)

        existing = db.query(GroupMember).filter(GroupMember.member_id == data.member_id).one_or_none()
        if existing:
            existing.group_id = data.group_id
            existing.role_department_id = data.role_department_id
            existing.joined_date = data.joined_date
            existing.is_active = True
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing

        new_gm = GroupMember(
            group_id=data.group_id,
            member_id=data.member_id,
            role_department_id=data.role_department_id,
            joined_date=data.joined_date,
            is_active=True,
        )
        db.add(new_gm)
        db.commit()
        db.refresh(new_gm)
        return new_gm

    def record_group_attendance(self, db: Session, *, data: GroupAttendanceCreate) -> GroupAttendanceSchema:
        self.repo.get_by_id(db=db, id=data.group_id)

        existing = (
            db.query(GroupAttendance)
            .filter(GroupAttendance.group_id == data.group_id)
            .filter(GroupAttendance.attendance_date == data.attendance_date)
            .one_or_none()
        )
        if existing:
            existing.attendance_count = data.attendance_count
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return GroupAttendanceSchema.model_validate(existing, from_attributes=True)

        record = GroupAttendance(
            group_id=data.group_id,
            attendance_date=data.attendance_date,
            attendance_count=data.attendance_count,
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        return GroupAttendanceSchema.model_validate(record, from_attributes=True)


group_service = GroupService()

