import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. Database URL define karein
DATABASE_URL = "sqlite:///./kaiee.db"

# 2. Engine create karein
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- TABLES DEFINITION ---
# Note: Hum models ko yahan import ya define karte hain taaki create_all unhe pehchaan sake
from app.auth.models import Base as UserBase

def setup_database():
    print("⏳ Creating database tables in kaiee.db...")
    try:
        # Saari tables create karo
        UserBase.metadata.create_all(bind=engine)
        print("✅ Success! Tables 'users' and others created successfully.")
    except Exception as e:
        print(f"❌ Error while creating tables: {e}")

if __name__ == "__main__":
    setup_database()