from typing import List, Literal, Optional

from fastapi import HTTPException, status
from pydantic import UUID4
from sqlalchemy import or_
from sqlalchemy.orm import Session, aliased

from domains.echurch.models.department import Department
from domains.echurch.models.group import Group, GroupMember
from domains.echurch.models.member import Member, Visitor
from domains.echurch.repositories.member import member_repo, visitor_repo
from domains.echurch.schemas.member import (
    MemberApprovalStatus,
    MemberCreate,
    MemberGroupInfoSchema,
    MemberListItemSchema,
    MemberSchema,
    MemberUpdate,
    VisitorCreate,
    VisitorSchema,
    VisitorUpdate,
)


class MemberService:
    def __init__(self):
        self.repo = member_repo
        self.visitor_repo = visitor_repo

    def list_members(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        approval_status: Optional[MemberApprovalStatus] = None,
        department_id: Optional[UUID4] = None,
        location_id: Optional[UUID4] = None,
        centre_id: Optional[UUID4] = None,
        order_by: Optional[str] = None,
        order_direction: Literal["asc", "desc"] = "asc",
    ) -> List[MemberListItemSchema]:
        RoleDept = aliased(Department)

        query = (
            db.query(Member, GroupMember, Group, RoleDept)
            .outerjoin(GroupMember, GroupMember.member_id == Member.id)
            .outerjoin(Group, Group.id == GroupMember.group_id)
            .outerjoin(RoleDept, RoleDept.id == GroupMember.role_department_id)
            .filter(Member.is_deleted.is_(False))
            .filter(Member.is_active.is_(True))
        )

        if approval_status:
            query = query.filter(Member.approval_status == approval_status)
        if department_id:
            query = query.filter(Member.department_id == department_id)
        if location_id:
            query = query.filter(Member.location_id == location_id)
        if centre_id:
            query = query.filter(Member.centre_id == centre_id)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Member.full_name.ilike(pattern),
                    Member.phone_number.ilike(pattern),
                    Member.email.ilike(pattern),
                )
            )

        if order_by:
            try:
                col = getattr(Member, order_by)
            except AttributeError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid order_by column: {order_by}",
                )
            query = query.order_by(col.desc() if order_direction == "desc" else col.asc())
        else:
            query = query.order_by(Member.created_date.desc())

        rows = query.offset(skip).limit(limit).all()
        items: List[MemberListItemSchema] = []
        for member, group_member, group, role_dept in rows:
            item = MemberListItemSchema.model_validate(member, from_attributes=True)
            if group_member and group:
                item.group = MemberGroupInfoSchema(
                    group_id=group.id,
                    group_name=group.name,
                    role_department_id=group_member.role_department_id,
                    role_department_name=role_dept.name if role_dept else None,
                )
            items.append(item)
        return items

    def create_member(self, db: Session, *, data: MemberCreate) -> MemberSchema:
        return self.repo.create(db=db, data=data, unique_fields=["email", "phone_number"])

    def update_member(self, db: Session, *, id: UUID4, data: MemberUpdate) -> MemberSchema:
        member = self.repo.get_by_id(db=db, id=id)
        return self.repo.update(db=db, db_obj=member, data=data, unique_fields=["email", "phone_number"])

    def get_member(self, db: Session, *, id: UUID4) -> MemberSchema:
        return self.repo.get_by_id(db=db, id=id)

    def delete_member(self, db: Session, *, id: UUID4, soft: bool = True) -> None:
        self.repo.delete(db=db, id=id, soft=soft)

    def set_member_approval_status(
        self, db: Session, *, id: UUID4, approval_status: MemberApprovalStatus
    ) -> MemberSchema:
        member = self.repo.get_by_id(db=db, id=id)
        member.approval_status = approval_status
        db.add(member)
        db.commit()
        db.refresh(member)
        return member

    # Visitors
    def list_visitors(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
    ) -> List[VisitorSchema]:
        query = db.query(Visitor).filter(Visitor.is_deleted.is_(False)).filter(Visitor.is_active.is_(True))
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Visitor.full_name.ilike(pattern),
                    Visitor.phone_number.ilike(pattern),
                    Visitor.email.ilike(pattern),
                )
            )
        return query.order_by(Visitor.created_date.desc()).offset(skip).limit(limit).all()

    def create_visitor(self, db: Session, *, data: VisitorCreate) -> VisitorSchema:
        return self.visitor_repo.create(db=db, data=data, unique_fields=["email", "phone_number"])

    def update_visitor(self, db: Session, *, id: UUID4, data: VisitorUpdate) -> VisitorSchema:
        visitor = self.visitor_repo.get_by_id(db=db, id=id)
        return self.visitor_repo.update(db=db, db_obj=visitor, data=data, unique_fields=["email", "phone_number"])

    def delete_visitor(self, db: Session, *, id: UUID4, soft: bool = True) -> None:
        self.visitor_repo.delete(db=db, id=id, soft=soft)


member_service = MemberService()

