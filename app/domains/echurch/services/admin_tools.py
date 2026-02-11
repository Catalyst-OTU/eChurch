import json
from datetime import date, datetime, time
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from domains.auth.models.role_permissions import Role
from domains.auth.models.users import User
from domains.echurch.models.attendance import FollowUpTemplate, MemberAttendance
from domains.echurch.models.backup import BackupSnapshot
from domains.echurch.models.centre import Centre
from domains.echurch.models.department import Department
from domains.echurch.models.event import ChurchEvent
from domains.echurch.models.finance import GivingTransaction
from domains.echurch.models.group import Group, GroupAttendance, GroupMember
from domains.echurch.models.location import Location
from domains.echurch.models.member import Member, Visitor
from domains.echurch.models.staff import Staff
from domains.echurch.repositories.backup import backup_snapshot_repo
from domains.echurch.schemas.admin_tools import (
    BackupCreateRequest,
    BackupRestoreResponse,
    BackupSnapshotDetailSchema,
    BackupSnapshotSchema,
    UserRoleItem,
)


def _json_safe(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date, time)):
        return value.isoformat()
    return value


def _model_to_dict(obj: Any) -> Dict[str, Any]:
    data = {}
    for col in obj.__table__.columns:
        data[col.name] = _json_safe(getattr(obj, col.name))
    return data


def _maybe_uuid(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    try:
        return UUID(value)
    except Exception:
        return value


class AdminToolsService:
    BACKUP_VERSION = "1"

    def list_user_roles(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[UserRoleItem]:
        rows = (
            db.query(
                User.id.label("user_id"),
                User.email.label("email"),
                User.role_id.label("role_id"),
                Role.name.label("role_name"),
                Staff.full_name.label("full_name"),
            )
            .outerjoin(Role, Role.id == User.role_id)
            .outerjoin(Staff, Staff.user_id == User.id)
            .order_by(User.created_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        items: List[UserRoleItem] = []
        for row in rows:
            name = row.full_name or (row.email.split("@")[0] if row.email else "User")
            items.append(
                UserRoleItem(
                    user_id=row.user_id,
                    name=name,
                    email=row.email,
                    role_id=row.role_id,
                    role_name=row.role_name,
                )
            )
        return items

    def update_user_role(self, db: Session, *, user_id: UUID, role_id: UUID) -> UserRoleItem:
        user = db.query(User).filter(User.id == user_id).one_or_none()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        role = db.query(Role).filter(Role.id == role_id).one_or_none()
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")

        user.role_id = role_id
        db.add(user)
        db.commit()
        db.refresh(user)

        staff = db.query(Staff).filter(Staff.user_id == user.id).one_or_none()
        name = staff.full_name if staff else (user.email.split("@")[0] if user.email else "User")
        return UserRoleItem(
            user_id=user.id,
            name=name,
            email=user.email,
            role_id=user.role_id,
            role_name=role.name,
        )

    def create_backup(self, db: Session, *, data: BackupCreateRequest, current_user: Optional[User]) -> BackupSnapshotSchema:
        payload = {
            "version": self.BACKUP_VERSION,
            "exported_at": datetime.utcnow().isoformat(),
            "tables": {
                "departments": [_model_to_dict(x) for x in db.query(Department).all()],
                "locations": [_model_to_dict(x) for x in db.query(Location).all()],
                "centres": [_model_to_dict(x) for x in db.query(Centre).all()],
                "members": [_model_to_dict(x) for x in db.query(Member).all()],
                "visitors": [_model_to_dict(x) for x in db.query(Visitor).all()],
                "groups": [_model_to_dict(x) for x in db.query(Group).all()],
                "group_members": [_model_to_dict(x) for x in db.query(GroupMember).all()],
                "group_attendance": [_model_to_dict(x) for x in db.query(GroupAttendance).all()],
                "member_attendance": [_model_to_dict(x) for x in db.query(MemberAttendance).all()],
                "follow_up_templates": [_model_to_dict(x) for x in db.query(FollowUpTemplate).all()],
                "events": [_model_to_dict(x) for x in db.query(ChurchEvent).all()],
                "giving_transactions": [_model_to_dict(x) for x in db.query(GivingTransaction).all()],
                "staff": [_model_to_dict(x) for x in db.query(Staff).all()],
            },
        }

        snapshot = BackupSnapshot(
            version=self.BACKUP_VERSION,
            notes=data.notes,
            payload=payload,
            created_by_user_id=current_user.id if current_user else None,
        )
        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)
        return BackupSnapshotSchema.model_validate(snapshot, from_attributes=True)

    def list_backups(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[BackupSnapshotSchema]:
        items = backup_snapshot_repo.get_all(db=db, skip=skip, limit=limit)
        return [BackupSnapshotSchema.model_validate(x, from_attributes=True) for x in items]

    def get_backup_detail(self, db: Session, *, id: UUID) -> BackupSnapshotDetailSchema:
        snapshot = backup_snapshot_repo.get_by_id(db=db, id=id)
        return BackupSnapshotDetailSchema.model_validate(snapshot, from_attributes=True)

    def restore_backup(self, db: Session, *, file: UploadFile) -> BackupRestoreResponse:
        raw = file.file.read()
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid backup JSON file")

        tables: Dict[str, List[Dict[str, Any]]] = payload.get("tables", {})

        restore_order = [
            ("departments", Department),
            ("locations", Location),
            ("centres", Centre),
            ("members", Member),
            ("visitors", Visitor),
            ("groups", Group),
            ("group_members", GroupMember),
            ("group_attendance", GroupAttendance),
            ("member_attendance", MemberAttendance),
            ("follow_up_templates", FollowUpTemplate),
            ("events", ChurchEvent),
            ("giving_transactions", GivingTransaction),
            ("staff", Staff),
        ]

        for table_name, model in restore_order:
            records = tables.get(table_name, [])
            for record in records:
                record = dict(record)
                # UUID conversions
                for key, value in list(record.items()):
                    if key == "id" or key.endswith("_id"):
                        record[key] = _maybe_uuid(value)

                # Parse timestamps/dates if present
                for k in ("created_date", "updated_date", "deleted_at", "refunded_at", "sent_at"):
                    if record.get(k):
                        try:
                            record[k] = datetime.fromisoformat(record[k])
                        except Exception:
                            pass
                for k in ("joined_date", "attendance_date", "event_date", "transaction_date"):
                    if record.get(k):
                        try:
                            record[k] = date.fromisoformat(record[k])
                        except Exception:
                            pass
                if record.get("event_time"):
                    try:
                        record["event_time"] = time.fromisoformat(record["event_time"])
                    except Exception:
                        pass

                existing = None
                if record.get("id"):
                    existing = db.query(model).filter(model.id == record["id"]).one_or_none()
                if existing:
                    for key, value in record.items():
                        if key == "id":
                            continue
                        if hasattr(existing, key):
                            setattr(existing, key, value)
                    db.add(existing)
                else:
                    try:
                        obj = model(**{k: v for k, v in record.items() if hasattr(model, k)})
                        db.add(obj)
                    except Exception:
                        # Skip invalid rows
                        continue
            db.commit()

        return BackupRestoreResponse(message="Restore completed")


admin_tools_service = AdminToolsService()
