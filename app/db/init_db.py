from .session import SessionLocal
from app.db.base import Base
from app.db.session import engine

# 🔥 VERY IMPORTANT: force model loading
import app.auth.models
import app.tenants.models
import app.tools.whatsapp.models

def init_db():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")