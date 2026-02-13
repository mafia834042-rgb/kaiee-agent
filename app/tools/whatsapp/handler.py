import os
import json
import requests
import datetime
import base64
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import Session
from app.auth.models import User

# --- LOCAL IMPORTS ---
try:
    from app.tools.drive.drive_client import (
        upload_bytes_to_drive,
        get_drive_service,
        get_or_create_folder
    )
    from app.tools.sheets.sheets_manager import (
        create_master_sheet,
        append_row_to_sheet
    )
except ImportError:
    from tools.drive.drive_client import upload_bytes_to_drive, get_drive_service, get_or_create_folder
    from tools.sheets.sheets_manager import create_master_sheet, append_row_to_sheet


# --- ENV CONFIG ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TWILIO_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
NGROK_URL = os.getenv("NGROK_URL")


# ----------------------------------------
# 🔹 JSON CLEANER
# ----------------------------------------
def clean_json_string(json_str: str):
    try:
        if "```json" in json_str:
            return json_str.split("```json")[1].split("```")[0].strip()
        elif "```" in json_str:
            return json_str.split("```")[1].strip()
        return json_str.strip()
    except Exception:
        return json_str


# ----------------------------------------
# 🔹 GEMINI API CALLER (FIXED VERSION)
# ----------------------------------------

def call_gemini_vision_api(prompt: str, image_bytes=None):
    if not GEMINI_API_KEY:
        print("❌ GEMINI_API_KEY missing")
        return None

    model_name = "gemini-2.5-flash"

    url = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={GEMINI_API_KEY}"

    headers = {"Content-Type": "application/json"}

    parts = [{"text": prompt}]

    if image_bytes:
        parts.append({
            "inline_data": {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(image_bytes).decode("utf-8")
            }
        })

    payload = {"contents": [{"parts": parts}]}

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)

        print("STATUS:", response.status_code)

        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.text)
            return None

    except Exception as e:
        print("Connection Error:", str(e))
        return None


# ----------------------------------------
# 🔹 MAIN WHATSAPP HANDLER
# ----------------------------------------
async def handle_whatsapp_message(
    message_body: str,
    sender_phone: str,
    media_url: str,
    db: Session
):

    print(f"\n📩 Processing request from: {sender_phone}")

    clean_phone = sender_phone.replace("whatsapp:", "").replace("+", "").strip()

    user = db.query(User).filter(User.phone_number == clean_phone).first()

    # ----------------------------------------
    # 🔐 If Not Logged In
    # ----------------------------------------
    if not user or not user.google_access_token:

        if not NGROK_URL:
            return "⚠️ Server config error. Contact admin."

        login_link = f"{NGROK_URL}/auth/google/login?phone={clean_phone}"

        return f"👋 Please login to continue:\n👉 {login_link}"

    # ----------------------------------------
    # 📊 Ensure Sheet Exists
    # ----------------------------------------
    sheet_id = user.spreadsheet_id

    if not sheet_id:
        try:
            print("📝 Creating new sheet...")
            sheet_id = create_master_sheet(user, f"Kaiee_Expenses_{clean_phone}")
            user.spreadsheet_id = sheet_id
            db.commit()
        except Exception as e:
            print(f"❌ Sheet creation failed: {e}")
            return "⚠️ Sheet create nahi ho payi."

    # ----------------------------------------
    # 📂 Drive Service Init
    # ----------------------------------------
    try:
        drive_service = get_drive_service(
            user.google_access_token,
            user.google_refresh_token
        )
    except Exception as e:
        print(f"❌ Drive service error: {e}")
        return "⚠️ Google Drive connect nahi ho paaya."

    # ----------------------------------------
    # 📸 IMAGE FLOW
    # ----------------------------------------
    if media_url:

        print("📸 Downloading image from Twilio...")

        try:
            img_res = requests.get(
                media_url,
                auth=HTTPBasicAuth(TWILIO_SID, TWILIO_TOKEN),
                timeout=15
            )

            if img_res.status_code != 200:
                return "⚠️ Image download failed."

            print("🧠 Sending to Gemini AI...")

            prompt = (
                "Extract JSON in this format only:\n"
                "{date, vendor, total_amount, category}\n"
                "Return only JSON."
            )

            ai_result = call_gemini_vision_api(prompt, img_res.content)

            data = {
                "date": str(datetime.date.today()),
                "vendor": "Unknown",
                "total_amount": "0",
                "category": "Unsorted"
            }

            if ai_result and "candidates" in ai_result:
                try:
                    text_output = ai_result["candidates"][0]["content"]["parts"][0]["text"]
                    parsed = json.loads(clean_json_string(text_output))
                    data.update(parsed)
                    print(f"✅ AI Extracted: {data}")
                except Exception as e:
                    print(f"⚠️ JSON parsing failed: {e}")

            # Create Folder
            main_folder = get_or_create_folder(
                "Kaiee_Team_Data",
                None,
                drive_service
            )

            filename = f"Bill_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

            upload = upload_bytes_to_drive(
                img_res.content,
                filename,
                main_folder,
                {
                    "access_token": user.google_access_token,
                    "refresh_token": user.google_refresh_token
                }
            )

            row = [
                data["date"],
                data["vendor"],
                "-",
                data["category"],
                "-",
                str(data["total_amount"]),
                "0",
                upload.get("view_link", "N/A"),
                "Admin"
            ]

            append_row_to_sheet(user, sheet_id, "Expenses", row)

            return (
                f"✅ Bill Saved!\n"
                f"🏢 {data['vendor']}\n"
                f"💰 ₹{data['total_amount']}"
            )

        except Exception as e:
            print(f"❌ Full image flow error: {e}")
            return "⚠️ Bill process nahi ho paaya."

    # ----------------------------------------
    # TEXT FLOW
    # ----------------------------------------
    return "✅ Ready! Bill bhejein."