from sqlalchemy.orm import Session
from app.auth.models import User
from app.auth.security import hash_password, verify_password
from app.auth.jwt import create_access_token

def create_user(db: Session, email: str, password: str, tenant_id: int):
    user = User(
        email=email,
        password_hash=hash_password(password),
        tenant_id=tenant_id,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    token = create_access_token({
        "sub": str(user.id),          # MUST be string
        "tenant_id": user.tenant_id
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }