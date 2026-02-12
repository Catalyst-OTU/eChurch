from fastapi import Request, Depends
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from config.logger import log
from config.settings import settings
from utils.core import change_database_schema
from email.generator import Generator
# Use psycopg2 for synchronous connections

# Create a synchronous engine
engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, echo=False)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db 
    finally:
        db.close()


def drop_and_alter_table_columns(db: Session):
    # the query execution
    result = db.execute(text('SELECT email FROM public.users'))
    set_results = result.scalars().all()
    schema : str = "public"
    
    if set_results:
        try:
            # the execution of the DDL command
            db.execute(text(f'ALTER TABLE "{schema}".users ADD COLUMN username VARCHAR(100) default null'))
            # First add the user_id column to members table
            db.execute(text(f'ALTER TABLE "{schema}".members ADD COLUMN user_id UUID'))
            # Then add the foreign key constraint
            db.execute(text(f'ALTER TABLE "{schema}".members ADD CONSTRAINT member_users_id_fkey FOREIGN KEY (user_id) REFERENCES "{schema}".users(id) ON DELETE SET NULL'))
            db.commit()
            print("Table altered successfully")
        except Exception as e:
            db.rollback()
            print(f"Error altering table: {e}")
    else:
        print("No results found, table alteration skipped")


