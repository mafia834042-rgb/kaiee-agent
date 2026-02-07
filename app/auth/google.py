import os
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow

# Aapke project ke internal imports
from app.db.session import get_db
from app.auth.models import User

router = APIRouter()

# --- Configuration ---
# Hum sirf File Upload ki permission mang rahe hain
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

def get_flow():
    """
    Environment variables se Google OAuth Flow create karta hai.
    """
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI")
    
    # Safety Check: Agar .env file load nahi hui toh error print karega
    if not client_id or not client_secret or not redirect_uri:
        print("❌ CRITICAL ERROR: .env file se Google Credentials load nahi huye!")
        return None

    return Flow.from_client_config(
        client_config={
            "web": {
                "client_id": client_id,
                "client_secret": client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri],
            }
        },
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )

@router.get("/auth/google/login")
def login(phone: str):
    """
    Step 1: User ko Google Login page par bhejta hai.
    """
    print(f"\n--- 🚀 LOGIN ATTEMPT START FOR: {phone} ---")
    
    try:
        flow = get_flow()
        if not flow:
            return "❌ Error: Server Configuration Missing (.env check karein)"
        
        # Authorization URL generate karein
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            state=phone  # Phone number ko state mein pass kiya
        )
        
        print(f"✅ Generated Google URL: {authorization_url}")
        return RedirectResponse(authorization_url)
    
    except Exception as e:
        print(f"❌ Error generating login URL: {str(e)}")
        return f"Error: {str(e)}"

@router.get("/auth/google/callback")
def callback(request: Request, db: Session = Depends(get_db)):
    """
    Step 2: Google se wapas aane par Token save karta hai.
    """
    print("\n--- 🔄 CALLBACK RECEIVED FROM GOOGLE ---")
    
    code = request.query_params.get("code")
    state_phone = request.query_params.get("state")
    error = request.query_params.get("error")

    # Error Handling
    if error:
        return f"❌ Google Error: {error}"

    if not code or not state_phone:
        return "❌ Error: Code or Phone number missing in callback."

    try:
        flow = get_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Database mein User dhundhein
        user = db.query(User).filter(User.phone_number == state_phone).first()
        
        if not user:
            print(f"👤 Creating new user for: {state_phone}")
            user = User(phone_number=state_phone)
            db.add(user)
        else:
            print(f"👤 Updating existing user: {state_phone}")
        
        # Tokens Save Karein
        user.google_access_token = credentials.token
        user.google_refresh_token = credentials.refresh_token
        
        db.commit()
        print("✅ Tokens saved successfully!")
        
        return "✅ Success! Aapki Drive connect ho gayi hai. Ab aap WhatsApp par files bhej sakte hain."
    
    except Exception as e:
        print(f"❌ Authentication Failed: {str(e)}")
        return f"Authentication Failed: {str(e)}"