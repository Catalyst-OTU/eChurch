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
    result = db.execute(text('SELECT username FROM users'))
    org_names = result.scalars().all()
    schema : str = "gi-kace"

    if org_names:
        # the execution of the DDL command
        db.execute(text(f'ALTER TABLE "{schema}".appraisal_inputs ADD COLUMN title VARCHAR(100) default null'))
        db.execute(text(f'ALTER TABLE "{schema}".appraisal_inputs ADD COLUMN description TEXT default null'))
        db.execute(text(f'ALTER TABLE "{schema}".appraisal_inputs RENAME COLUMN appraisal_id to appraisal_section_id'))
        db.execute(text(f'ALTER TABLE "{schema}".appraisal_inputs DROP CONSTRAINT appraisal_inputs_appraisal_id_fkey'))
        db.execute(text(f'ALTER TABLE "{schema}".appraisal_inputs ADD CONSTRAINT appraisal_inputs_appraisal_section_id_fkey FOREIGN KEY (appraisal_section_id) REFERENCES "{schema}".appraisal_sections(id) ON DELETE SET NULL'))
        db.commit()
        print("Table altered successfully")
    else:
        print("Table not found")


