from uuid import uuid4
from sqlalchemy.orm import Session
from sqlalchemy import select
from domains.auth.models.users import User
from passlib.context import CryptContext
from domains.auth.models.role_permissions import Role

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SystemAdmin:
    System_ADMIN_NAME: str = "System Administrator"
    System_ADMIN_EMAIL: str = "systemadmin@admin.com"
    System_ADMIN_PASSWORD: str = "openforme"


class SuperAdmin:
    Super_ADMIN_NAME: str = "Super Administrator"
    Super_ADMIN_EMAIL: str = "superadmin@admin.com"
    Super_ADMIN_PASSWORD: str = "openforme"


def create_system_admin(db: Session):
    """Creates System Admin and Super Admin users with their role."""

    # Check if the System Administrator role exists
    existing_role = db.execute(select(Role).where(Role.name == "System Administrator"))
    existing_role = existing_role.scalars().first()

    if not existing_role:
        system_admin_role = Role(id=uuid4(), name="System Administrator")
        db.add(system_admin_role)
        db.commit()
        db.refresh(system_admin_role)
    else:
        system_admin_role = existing_role


    
        # Check if the System Administrator role exists
    existing_member_role = db.execute(select(Role).where(Role.name == "Member"))
    existing_member_role = existing_member_role.scalars().first()

    if not existing_member_role:
        add_driver_role = Role(id=uuid4(), name="Member")
        db.add(add_driver_role)
        db.commit()
        db.refresh(add_driver_role)
    else:
        add_driver_role = existing_member_role




    existing_finance_manager_role = db.execute(select(Role).where(Role.name == "Finance Manager"))
    existing_finance_manager_role = existing_finance_manager_role.scalars().first()

    if not existing_finance_manager_role:
        system_admin_role = Role(id=uuid4(), name="Finance Manager")
        db.add(system_admin_role)
        db.commit()
        db.refresh(system_admin_role)
    else:
        system_admin_role = existing_finance_manager_role


    
        # Check if the System Administrator role exists
    existing_pastor_role = db.execute(select(Role).where(Role.name == "Pastor"))
    existing_pastor_role = existing_pastor_role.scalars().first()

    if not existing_pastor_role:
        add_driver_role = Role(id=uuid4(), name="Pastor")
        db.add(add_driver_role)
        db.commit()
        db.refresh(add_driver_role)
    else:
        add_driver_role = existing_pastor_role



    existing_worker_role = db.execute(select(Role).where(Role.name == "Worker"))
    existing_worker_role = existing_worker_role.scalars().first()

    if not existing_worker_role:
        add_worker_role = Role(id=uuid4(), name="Worker")
        db.add(add_worker_role)
        db.commit()
        db.refresh(add_worker_role)
    else:
        add_worker_role = existing_worker_role



    # Check if System Admin already exists
    result = db.execute(select(User).filter(User.email == SystemAdmin.System_ADMIN_EMAIL))
    system_admin = result.scalars().first()

    # Check if Super Admin already exists
    result = db.execute(select(User).filter(User.email == SuperAdmin.Super_ADMIN_EMAIL))
    super_admin = result.scalars().first()

    if system_admin or super_admin:
        return  # Exit
    


    system_admin_in = User(
        username=SystemAdmin.System_ADMIN_NAME,
        email=SystemAdmin.System_ADMIN_EMAIL,
        password=pwd_context.hash(SystemAdmin.System_ADMIN_PASSWORD),
        role_id = system_admin_role.id
    )

    db.add(system_admin_in)
    db.commit()
    db.refresh(system_admin_in)



    super_admin_in = User(
        username=SuperAdmin.Super_ADMIN_NAME,
        email=SuperAdmin.Super_ADMIN_EMAIL,
        password=pwd_context.hash(SuperAdmin.Super_ADMIN_PASSWORD),
        role_id = system_admin_role.id
    )

    db.add(super_admin_in)
    db.commit()
    db.refresh(super_admin_in)
