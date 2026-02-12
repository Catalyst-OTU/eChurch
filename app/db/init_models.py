import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import sessionmaker
from config.logger import log
from config.settings import settings
from db.base_class import APIBase
from db.session import engine

SQLALCHEMY_DATABASE_URL = settings.SQLALCHEMY_DATABASE_URL
# For creating the DB

def create_database():
    """Create the database if it does not exist (synchronously)."""
    if SQLALCHEMY_DATABASE_URL.startswith("postgresql"):
        db_name = SQLALCHEMY_DATABASE_URL.split("/")[-1]

        system_engine = create_engine(SQLALCHEMY_DATABASE_URL.rsplit("/", 1)[0] + "/postgres")
        
        with system_engine.connect() as conn:
            try:
                conn.execution_options(isolation_level="AUTOCOMMIT")

                result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
                if result.scalar():
                    return  # Database already exists, no need to create it

                conn.execute(text(f"CREATE DATABASE {db_name}"))
            except ProgrammingError:
                pass  # Ignore errors related to database creation

def init_database():
    """Initialize the database."""
    print("Starting database")
    create_database()






from domains.auth.models.refresh_token import RefreshToken
from domains.auth.models.users import User
from domains.auth.models.role_permissions import Role,Permission, role_permissions
from domains.echurch.models.department import Department
from domains.echurch.models.location import Location
from domains.echurch.models.centre import Centre
from domains.echurch.models.member import Member, Visitor
from domains.echurch.models.staff import Staff
from domains.echurch.models.group import Group, GroupMember, GroupAttendance
from domains.echurch.models.attendance import MemberAttendance, FollowUpTemplate
from domains.echurch.models.event import ChurchEvent
from domains.echurch.models.finance import GivingTransaction, AuditLog
from domains.echurch.models.messaging import OutboundMessage, OutboundMessageRecipient
from domains.echurch.models.backup import BackupSnapshot

def init_tables():
    selected_models = [
        Role,
        Permission,
        User,
        RefreshToken,

        # E-Church domain
        Department,
        Location,
        Centre,
        Member,
        Visitor,
        Staff,
        Group,
        GroupMember,
        GroupAttendance,
        MemberAttendance,
        FollowUpTemplate,
        ChurchEvent,
        GivingTransaction,
        AuditLog,
        OutboundMessage,
        OutboundMessageRecipient,
        BackupSnapshot,

    ]

    with engine.begin() as conn:
        for model in selected_models:
            model.__table__.schema = "public"
            model.__table__.create(bind=conn, checkfirst=True)

        # Ensure schema is set for the Table object
        role_permissions.schema = "public"
        role_permissions.create(bind=conn, checkfirst=True)

