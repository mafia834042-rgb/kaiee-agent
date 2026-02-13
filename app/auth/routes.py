from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
from app.database import get_db
# Ab hum sahi function import kar rahe hain jo humne Step 1 mein banaya
from app.auth.service import update_user_tokens, get_user_by_phone, create_user
from app.tools.sheets.google_client import get_google_auth_url, get_tokens_from_code

router = APIRouter()

@router.get("/google/login")
async def google_login(phone: str, db: Session = Depends(get_db)):
    # 1. User check karein, nahi hai toh bana dein
    user = get_user_by_phone(db, phone)
    if not user:
        create_user(db, {"phone_number": phone})
    
    # 2. Google Login Page par bhejein
    auth_url = get_google_auth_url(phone)
    return RedirectResponse(auth_url)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    code = request.query_params.get("code")
    state_phone = request.query_params.get("state") # Phone number wapas milega
    
    if not code or not state_phone:
        return "❌ Error: Google se code nahi mila."

    # 3. Tokens Exchange Karein
    tokens = get_tokens_from_code(code)
    
    if "error" in tokens:
        return f"❌ Error: {tokens['error']}"

    # 4. Database Update Karein
    update_user_tokens(
        db, 
        state_phone, 
        tokens["access_token"], 
        tokens.get("refresh_token"), # Refresh token optional hota hai
        None
    )
    
    return "✅ Tokens saved successfully! Ab aap WhatsApp par message bhej sakte hain."