# app/db/base.py
from app.db.session import Base

# FORCE IMPORT ALL MODELS
from app.auth.models import User
from app.tenants.models import Tenant
from app.tools.whatsapp.models import WhatsAppAccount