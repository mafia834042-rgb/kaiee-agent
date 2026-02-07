# FILE: app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database setup (Local file)
SQLALCHEMY_DATABASE_URL = "sqlite:///./kaiee.db"

# Engine Creation
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session Local class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class jo models use karenge
Base = declarative_base()

# Dependency - Ye har route mein DB session dega
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()