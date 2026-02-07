from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.auth.service import create_user, authenticate_user
from app.auth.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup")
def signup(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")
    tenant_id = payload.get("tenant_id")

    if not email or not password or not tenant_id:
        raise HTTPException(status_code=400, detail="Missing fields")

    return create_user(db, email, password, tenant_id)

@router.post("/login")
def login(payload: dict, db: Session = Depends(get_db)):
    email = payload.get("email")
    password = payload.get("password")

    result = authenticate_user(db, email, password)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return result

@router.get("/me")
def me(current_user=Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "tenant_id": current_user.tenant_id,
        "is_active": current_user.is_active
    }