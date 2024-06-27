from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import Depends


DATABASE_URL = "sqlite:///./data.spsql"  # TODO Use Docker volume for this path

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
_db = SessionLocal()


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    try:
        yield _db
    finally:
        _db.close_all()


DB_SESSION: Session = Depends(get_db)
