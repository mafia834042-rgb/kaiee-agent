import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 1. Database URL nikalo (Render se ya Local se)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Logic: Agar Render ka URL hai toh Postgres use karo, nahi toh Local SQLite
if DATABASE_URL:
    # Render "postgres://" deta hai, lekin SQLAlchemy ko "postgresql://" chahiye
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Cloud Database Connection
    engine = create_engine(DATABASE_URL)
else:
    # Local Laptop Connection (SQLite)
    DATABASE_URL = "sqlite:///./kaiee.db"
    # SQLite ke liye special setting
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 3. Session aur Base setup
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 4. Dependency (Har request ke liye DB dena)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()