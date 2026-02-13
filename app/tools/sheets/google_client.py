import os
import json
from google_auth_oauthlib.flow import Flow

# --- CONFIGURATION ---
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file'
]

def get_client_config():
    """Environment variables se Google Config banata hai"""
    return {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID"),
            "project_id": "kaiee-agent",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
            "redirect_uris": [f"{os.getenv('NGROK_URL')}/auth/google/callback"]
        }
    }

# --- LOGIN URL GENERATOR ---
def get_google_auth_url(phone_number: str):
    """
    User ke liye Login Link banata hai.
    'state' parameter mein phone number chupata hai taaki wapas aane par user pehchana jaye.
    """
    config = get_client_config()
    
    flow = Flow.from_client_config(
        config,
        scopes=SCOPES,
        redirect_uri=config['web']['redirect_uris'][0]
    )
    
    # 'prompt=consent' zaroori hai taaki Refresh Token hamesha mile
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
        state=phone_number
    )
    
    return auth_url

# --- TOKEN EXCHANGER ---
def get_tokens_from_code(code: str):
    """Google se mile 'Code' ko badle mein 'Tokens' leta hai"""
    config = get_client_config()
    
    flow = Flow.from_client_config(
        config,
        scopes=SCOPES,
        redirect_uri=config['web']['redirect_uris'][0]
    )
    
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        
        return {
            "access_token": creds.token,
            "refresh_token": creds.refresh_token, # Ye sabse zaroori cheez hai!
            "token_uri": creds.token_uri,
            "scopes": creds.scopes
        }
    except Exception as e:
        return {"error": str(e)}