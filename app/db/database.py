from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATABASE_URL = "sqlite:///data/data.spsql"  # TODO Use Docker volume for this path

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=True, bind=engine)
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
