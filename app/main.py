# FILE: app/main.py
from fastapi import FastAPI
from dotenv import load_dotenv  # <--- Ye line add karein
import os                       # <--- Ye line add karein

# 1. Sabse pehle .env load karein
load_dotenv() 

# Debugging: Check karein ki ID load hui ya nahi (Ye Terminal mein print hoga)
print("---------------------------------------------------")
print(f"DEBUG CHECK: Client ID loaded? -> {os.getenv('GOOGLE_CLIENT_ID')}")
print("---------------------------------------------------")

# ... baaki code same rahega ...
from app.auth.google import router as google_router
from app.tools.whatsapp.routes import router as whatsapp_router

app = FastAPI()
# ... include routers ...
from fastapi import FastAPI
from app.auth.google import router as google_router
from app.tools.whatsapp.routes import router as whatsapp_router

app = FastAPI()

app.include_router(google_router)
app.include_router(whatsapp_router)