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
from domains.etransport.models.driver import Driver
from domains.etransport.models.vehicle import Vehicle
from domains.etransport.models.passenger import Passenger
from domains.etransport.models.trip import Trip, TripCancellation
from domains.etransport.models.rating import Rating
from domains.etransport.models.transaction import Transaction
from domains.etransport.models.admin_action_log import AdminActionLog
from domains.etransport.models.notification import Notification
from domains.etransport.models.chat import ChatMessage

def init_tables():
    selected_models = [
        Role,
        User,
        RefreshToken,
        Permission,
        # Vehicle,
        # Driver,
        # Passenger,
        # Trip,
        # Rating,
        # Transaction,
        # AdminActionLog,
        # Notification,
        # TripCancellation,
        # ChatMessage
    ]

    with engine.begin() as conn:
        for model in selected_models:
            model.__table__.schema = "public"
            model.__table__.create(bind=conn, checkfirst=True)

        # Ensure schema is set for the Table object
        role_permissions.schema = "public"
        role_permissions.create(bind=conn, checkfirst=True)


