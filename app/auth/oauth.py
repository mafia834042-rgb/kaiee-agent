from app.core.security import create_access_token

def login_with_google(email: str, tenant_id: int):
    token = create_access_token({
        "user_id": email,
        "tenant_id": tenant_id
    })
    return {
        "access_token": token,
        "token_type": "bearer"
    }
