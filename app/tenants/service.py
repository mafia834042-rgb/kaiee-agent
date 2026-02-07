import os
from sqlalchemy.orm import Session
from app.tenants.models import Tenant
from app.config import TENANTS_DIR

def create_tenant(db: Session, company_name: str):
    tenant = Tenant(name=company_name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)

    tenant_path = os.path.join(TENANTS_DIR, f"tenant_{tenant.id}")
    os.makedirs(os.path.join(tenant_path, "agents"), exist_ok=True)
    os.makedirs(os.path.join(tenant_path, "files"), exist_ok=True)
    os.makedirs(os.path.join(tenant_path, "logs"), exist_ok=True)

    print(f"✅ Tenant folder created at: {tenant_path}")
    return tenant
