from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.auth.models import User
from app.tools.sheets.sheets_manager import create_master_sheet
from app.tools.drive.drive_client import get_drive_service, get_or_create_folder

# Database Connect
engine = create_engine("sqlite:///kaiee.db")
Session = sessionmaker(bind=engine)
db = Session()

# Pehla User uthao (Jo abhi login hua tha)
user = db.query(User).first()

if not user:
    print("❌ KOI USER NAHI MILA! Pehle Login karo.")
else:
    print(f"👤 User Mila: {user.phone_number}")
    print("🚀 Sheet banane ki koshish kar raha hu...")

    try:
        # 1. Folder Check
        print("1️⃣  Folder dhund raha hu...")
        drive_service = get_drive_service(user.google_access_token, user.google_refresh_token)
        folder_id = get_or_create_folder("Kaiee_Team_Data", None, drive_service)
        print(f"✅ Folder ID: {folder_id}")
        
        # 2. Sheet Create
        print("2️⃣  Sheet bana raha hu (Ye 5 sec lega)...")
        sheet_id = create_master_sheet(user, folder_id)
        
        print("\n" + "="*40)
        print(f"🎉 SUCCESS! Sheet Ban Gayi!")
        print(f"🔗 Link: https://docs.google.com/spreadsheets/d/{sheet_id}")
        print("="*40)
        
        # Save to DB
        user.spreadsheet_id = sheet_id
        db.commit()
        print("💾 Database Update Ho Gaya.")
        
    except Exception as e:
        print("\n🛑 ERROR PAKDA GAYA:")
        print(e)