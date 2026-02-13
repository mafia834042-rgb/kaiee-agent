from sqlalchemy.orm import Session
from app.auth.models import User

# --- USER CREATE KARNA ---
def get_user_by_phone(db: Session, phone: str):
    return db.query(User).filter(User.phone_number == phone).first()

def create_user(db: Session, user_data: dict):
    # Check agar user pehle se hai
    existing_user = get_user_by_phone(db, user_data["phone_number"])
    if existing_user:
        return existing_user
    
    # Naya User Banao
    new_user = User(
        phone_number=user_data["phone_number"],
        role=user_data.get("role", "admin"),
        # Baki fields default rahenge
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# --- USER UPDATE KARNA (TOKENS) ---
def update_user_tokens(db: Session, phone: str, access_token: str, refresh_token: str, spreadsheet_id: str = None):
    user = get_user_by_phone(db, phone)
    if user:
        user.google_access_token = access_token
        if refresh_token: # Sirf tab update karein agar naya mila ho
            user.google_refresh_token = refresh_token
        if spreadsheet_id:
            user.spreadsheet_id = spreadsheet_id
            
        db.commit()
        db.refresh(user)
    return user