import os
from pathlib import Path
from dotenv import load_dotenv

# 🔥 FORCE load .env from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR.parent / ".env")

# ===== TWILIO =====
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

# ===== GOOGLE DRIVE =====
GOOGLE_DRIVE_FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

# ===== SAFETY CHECKS =====
if not GOOGLE_DRIVE_FOLDER_ID:
    raise RuntimeError("❌ GOOGLE_DRIVE_FOLDER_ID missing from .env")