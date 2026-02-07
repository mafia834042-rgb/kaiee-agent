from app.db.session import engine, Base

# 🔥 FORCE REGISTER ALL MODELS
from app.auth.models import User
from app.tenants.models import Tenant
from app.tools.whatsapp.models import WhatsAppAccount


def init_db():
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("Done")


if __name__ == "__main__":
    init_db()