from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.tenants.service import create_tenant

router = APIRouter(
    prefix="/tenants",
    tags=["Tenants"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("")
def create_tenant_api(payload: dict, db: Session = Depends(get_db)):
    name = payload.get("name")
    return create_tenant(db, name)
