import os
import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import Session
from app.auth.models import User
from app.tools.drive.drive_client import upload_bytes_to_drive, get_drive_service, get_or_create_folder

async def handle_whatsapp_message(message_body: str, sender_phone: str, media_url: str, db: Session):
    
    # 1. User Check (Sender kaun hai?)
    user = db.query(User).filter(User.phone_number == sender_phone).first()

    # --- Scenario A: Naya User (Na Admin hai, na Worker) ---
    if not user:
        # Default behavior: Naya user banao (as Admin candidate)
        user = User(phone_number=sender_phone, role="admin")
        db.add(user)
        db.commit()
        
        # Login Link bhejo
        ngrok_url = "https://tenurial-cher-dubitably.ngrok-free.dev" # <--- Apna URL check kar lena
        auth_link = f"{ngrok_url}/auth/google/login?phone={sender_phone}"
        return f"👋 Welcome! Setup ke liye Drive connect karein: {auth_link}"

    # --- Scenario B: Admin Commands (Workers Add karna) ---
    # Command Format: "Add worker 919876543210"
    if message_body.lower().startswith("add worker"):
        if user.role != "admin":
            return "❌ Access Denied: Sirf Admin workers add kar sakta hai."
        
        try:
            # Number nikalo message se
            worker_phone = message_body.split(" ")[2].strip().replace("+", "")
            
            # Check karo worker pehle se hai kya
            worker = db.query(User).filter(User.phone_number == worker_phone).first()
            
            if worker:
                worker.role = "employee"
                worker.parent_admin_id = user.id
                worker.google_access_token = None # Worker ko token ki zaroorat nahi
            else:
                worker = User(
                    phone_number=worker_phone, 
                    role="employee", 
                    parent_admin_id=user.id
                )
                db.add(worker)
            
            db.commit()
            return f"✅ Success! Worker ({worker_phone}) add ho gaya.\nAb wo jo bhi bhejega, aapki Drive mein aayega."
            
        except IndexError:
            return "❌ Galat Command. Aise likhein: 'Add worker 9199999999'"

    # --- Scenario C: File Upload Logic (Role-Based) ---
    if media_url:
        print(f"📥 Processing upload for: {sender_phone} (Role: {user.role})")
        
        # 1. PEHCHAAN: Kiska Token aur Kiska Folder use karna hai?
        if user.role == "employee":
            # Agar Worker hai -> Boss ko dhundo
            boss = db.query(User).filter(User.id == user.parent_admin_id).first()
            if not boss or not boss.google_access_token:
                return "❌ Error: Aapke Boss ne Drive connect nahi ki hai."
            
            target_user = boss        # Token Boss ka
            folder_name = f"Worker_{sender_phone}" # Folder Worker ka
        
        else:
            # Agar Admin hai -> Khud ka use karo
            if not user.google_access_token:
                ngrok_url = "https://tenurial-cher-dubitably.ngrok-free.dev"
                auth_link = f"{ngrok_url}/auth/google/login?phone={sender_phone}"
                return f"⚠️ Pehle Drive connect karein: {auth_link}"
                
            target_user = user
            folder_name = "My_Uploads"

        # 2. DOWNLOAD (Twilio)
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        
        try:
            response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))
            if response.status_code == 200:
                file_bytes = response.content
                filename = f"img_{os.urandom(4).hex()}.jpg"
                
                # 3. SMART FOLDER LOGIC
                # Service Boss ke token se banegi
                service = get_drive_service(target_user.google_access_token, target_user.google_refresh_token)
                
                # Main App Folder
                main_folder_id = get_or_create_folder("Kaiee_Team_Data", None, service)
                
                # Target Folder (Worker ya Admin ka folder)
                final_folder_id = get_or_create_folder(folder_name, main_folder_id, service)
                
                # 4. UPLOAD
                tokens = {
                    "access_token": target_user.google_access_token,
                    "refresh_token": target_user.google_refresh_token
                }
                
                result = upload_bytes_to_drive(
                    file_bytes=file_bytes,
                    file_name=filename,
                    folder_id=final_folder_id,
                    user_tokens=tokens
                )
                
                if result:
                    return f"✅ Saved to '{folder_name}'! Link: {result.get('view_link')}"
                else:
                    return "❌ Upload failed."
            else:
                return "❌ Download failed."
        except Exception as e:
            return f"❌ Error: {str(e)}"

    return "Kripya photo bhejein ya 'Add worker [number]' likhein."