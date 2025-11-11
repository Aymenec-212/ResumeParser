# app/core/db.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Create the SQLAlchemy engine
engine = create_engine(
    settings.SQLALCHEMY_DATABASE_URL,
    # connect_args is needed only for SQLite
    connect_args={"check_same_thread": False}
)

# Each instance of the SessionLocal class will be a database session.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This Base class will be used by our models to inherit from.
Base = declarative_base()

# Dependency to get a DB session for our API endpoints
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()