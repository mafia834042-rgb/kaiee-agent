import os
import re
import requests
import datetime
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import Session
from app.auth.models import User
from app.tools.drive.drive_client import upload_bytes_to_drive, get_drive_service, get_or_create_folder
from app.tools.sheets.sheets_manager import create_master_sheet, append_row_to_sheet

# --- ⚙️ SETTINGS ---
PLAN_LIMITS = {"free": 5, "pro": 100, "unlimited": 9999}

def parse_business_message(text):
    """Smart Parser: Message se Amount, Item aur Mode nikalta hai."""
    clean_text = text.lower().strip()
    
    # 1. AMOUNT 💰
    amount_match = re.search(r'\d+', clean_text)
    amount = amount_match.group() if amount_match else "0"

    # 2. PAYMENT MODE 💳
    payment_mode = "Cash"
    if any(w in clean_text for w in ["upi", "gpay", "phonepe", "paytm", "online", "bank", "qr"]):
        payment_mode = "Online/UPI"
    elif any(w in clean_text for w in ["card", "credit", "debit"]):
        payment_mode = "Card"

    # 3. ITEM NAME 📦
    remove_words = [
        amount, "expense", "spent", "paid", "kharcha", "buy", "bought", "cost", 
        "rs", "rupees", "inr", "sale", "sold", "income", "received", "got", "becha",
        "via", "through", "upi", "cash", "gpay", "online", "for", "by", "ka", "diya", "liya"
    ]
    description = clean_text
    for word in remove_words:
        description = description.replace(word, "")
    
    item_name = " ".join(description.split()).title()
    if not item_name or len(item_name) < 2: item_name = "General Item"
        
    return amount, item_name, payment_mode

async def handle_whatsapp_message(message_body: str, sender_phone: str, media_url: str, db: Session):
    print(f"\n📩 Message Received from {sender_phone}...") 
    
    # --- 1. USER CHECK ---
    user = db.query(User).filter(User.phone_number == sender_phone).first()

    if not user:
        user = User(phone_number=sender_phone, role="admin", plan_type="free")
        db.add(user)
        db.commit()
        ngrok_url = os.getenv("GOOGLE_REDIRECT_URI", "").split("/auth")[0]
        if "ngrok" not in ngrok_url: ngrok_url = "https://tenurial-cher-dubitably.ngrok-free.dev"
        return f"👋 Welcome! Setup Link: {ngrok_url}/auth/google/login?phone={sender_phone}"

    if user.role == "employee":
        target_user = db.query(User).filter(User.id == user.parent_admin_id).first()
        entered_by = f"Staff ({sender_phone[-4:]})"
        folder_name = f"Staff_{sender_phone}"
    else:
        target_user = user
        entered_by = "Admin (Owner)"
        folder_name = "Admin_Uploads"

    if not target_user or not target_user.google_access_token:
        return "❌ Error: Google Drive Not Connected."

    # --- 2. SHEET SETUP ---
    sheet_id = target_user.spreadsheet_id
    drive_service = get_drive_service(target_user.google_access_token, target_user.google_refresh_token)
    
    if not sheet_id:
        try:
            print("Creating Sheet...")
            main_folder_id = get_or_create_folder("Kaiee_Team_Data", None, drive_service)
            sheet_id = create_master_sheet(target_user, main_folder_id)
            target_user.spreadsheet_id = sheet_id
            db.commit()
            return f"🎉 System Ready! Sheet: https://docs.google.com/spreadsheets/d/{sheet_id}"
        except Exception as e:
            return f"❌ Setup Error: {str(e)}"

    # --- 3. TEXT MESSAGE HANDLER ---
    if not media_url:
        msg = message_body.lower().strip()
        today = str(datetime.date.today())
        
        if msg.startswith("add worker") and user.role == "admin":
             return "✅ Worker logic active."

        amount, item, mode = parse_business_message(message_body)
        
        if any(w in msg for w in ["spent", "paid", "expense", "kharcha", "buy", "bought", "cost"]):
            print(f"📝 Writing Expense: {item} - {amount}")
            append_row_to_sheet(target_user, sheet_id, "Expenses", [today, item, "General", amount, entered_by, ""])
            return f"✅ **Expense Saved!**\n📉 {item}: ₹{amount} ({mode})"

        elif any(w in msg for w in ["sold", "sale", "income", "received", "got"]):
            print(f"📝 Writing Sale: {item} - {amount}")
            append_row_to_sheet(target_user, sheet_id, "Sales", [today, "Walk-in", item, amount, mode, "Done", entered_by])
            return f"💰 **Sale Saved!**\n📈 {item}: ₹{amount} ({mode})"
        
        # Default fallback
        append_row_to_sheet(target_user, sheet_id, "Expenses", [today, item, "General", amount, entered_by, ""])
        return f"✅ **Saved!**\n{item}: ₹{amount}"

    # --- 4. PHOTO HANDLER (Fixed Link Extraction) 📷 ---
    if media_url:
        print("📸 Photo Detected! Processing...")
        
        # 1. Download
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        try:
            response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))
            if response.status_code == 200:
                print("✅ Photo Downloaded.")
                file_bytes = response.content
                filename = f"img_{datetime.datetime.now().strftime('%H%M%S')}.jpg"
                
                # 2. Upload to Drive
                print("🚀 Uploading to Drive...")
                main_folder_id = get_or_create_folder("Kaiee_Team_Data", None, drive_service)
                final_folder_id = get_or_create_folder(folder_name, main_folder_id, drive_service)
                
                tokens = {"access_token": target_user.google_access_token, "refresh_token": target_user.google_refresh_token}
                
                # FIX IS HERE 👇
                upload_response = upload_bytes_to_drive(file_bytes, filename, final_folder_id, tokens)
                
                # Link nikalne ka sahi tareeka
                file_link = None
                if isinstance(upload_response, dict):
                    file_link = upload_response.get("view_link")
                else:
                    file_link = upload_response # Agar direct string hui

                print(f"🔗 Correct Drive Link: {file_link}")
                
                if file_link:
                    # 3. Update Sheet
                    print("📊 Updating Sheet Row...")
                    today = str(datetime.date.today())
                    row = [today, "Photo Receipt", "Upload", "0", entered_by, file_link]
                    
                    try:
                        append_row_to_sheet(target_user, sheet_id, "Expenses", row)
                        print("✅ Sheet Updated Successfully!")
                        return f"✅ **Photo Saved!**\n📂 Check Drive & Sheet."
                    except Exception as e:
                        print(f"❌ SHEET ERROR: {e}")
                        return f"⚠️ Drive me hai, par Sheet fail hui: {e}"
                else:
                    print("❌ Drive Link None aaya.")
                    return "❌ Drive Upload Failed."
            else:
                return "❌ Media Download Failed."
        except Exception as e:
            print(f"❌ CRITICAL ERROR: {e}")
            return f"❌ Error: {str(e)}"