from sqlalchemy import Column, Integer, String
from app.db.session import Base   # ✅ SAME BASE

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)