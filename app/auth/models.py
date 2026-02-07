# FILE: app/auth/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True)
    
    # --- 1. SaaS & Role Management ---
    role = Column(String, default="admin")  # 'admin' ya 'employee'
    
    # Agar ye Employee hai, to iska Boss kaun hai? (Boss ki ID)
    parent_admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # --- 2. Google OAuth Credentials ---
    # Sirf Admin ke paas Tokens honge. Employees Boss ka Token use karenge.
    google_access_token = Column(String, nullable=True)
    google_refresh_token = Column(String, nullable=True)
    
    # --- 3. Smart Folder Management ---
    # Admin ka Main Folder ID
    drive_folder_id = Column(String, nullable=True) 
    
    # --- 4. Quota & Limits (Paisa Vasool) ---
    plan_type = Column(String, default="free")  # 'free', 'pro', 'business'
    upload_count = Column(Integer, default=0)   # Aaj kitni files bheji
    last_reset_date = Column(DateTime, default=datetime.utcnow) # Quota kab reset hua
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships (Optional: Future use ke liye)
    # employees = relationship("User")