import os
import sys

# 1. SETUP PATHS
current_dir = os.getcwd()
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 2. ASK THE ENGINE: "DATABASE KAHAN HAI?"
from app.db.session import engine, SessionLocal, Base
# Models import zaroori hai
from app.tenants.models import Tenant
from app.tools.whatsapp.models import WhatsAppAccount
from app.tools.whatsapp.handler import handle_whatsapp_message

print("\n🕵️  SHERLOCK MODE: Asli Database Dhoondh Raha Hoon...")

# Engine se puchte hain ki URL kya hai
db_url = str(engine.url)
print(f"🔌 Connection URL: {db_url}")

# URL se File Path nikalna
if "sqlite" in db_url:
    # URL safai (sqlite:/// hatao)
    db_filename = db_url.replace("sqlite:///", "").replace("sqlite://", "")
    
    # Full Path banate hain
    real_db_path = os.path.abspath(db_filename)
    print(f"📂 TARGET FILE: {real_db_path}")
    
    # AB DELETE KARO
    if os.path.exists(real_db_path):
        print(f"🚨 PAKDA GAYA! Deleting {db_filename}...")
        try:
            # Engine band karke delete karte hain
            engine.dispose()
            os.remove(real_db_path)
            print("🗑️  SUCCESS: Asli Database Delete Kar Diya!")
        except Exception as e:
            print(f"❌ Delete nahi hua: {e}")
    else:
        print("⚠️ Ajeeb baat hai, file wahan nahi dikh rahi.")
else:
    print("ℹ️  Ye SQLite nahi lag raha.")

# 3. RECREATE FRESH SYSTEM
print("\n🏗️  Naya Database Bana Raha Hoon...")
Base.metadata.create_all(bind=engine)
print("✅ Tables Created (Created_at column ke saath).")

# 4. FINAL TEST
db = SessionLocal()
try:
    print("⏳ Creating Tenant...")
    tenant = Tenant(name="Kaiee AI Pvt Ltd", id=1)
    db.add(tenant)
    db.commit()
    print("✅ Tenant 1 Created.")
    
    print("\n🚀 Testing WhatsApp...")
    result = handle_whatsapp_message(
        db=db,
        phone_number="+919999999999",
        user_id=1,
        tenant_id=1,
        message="status"
    )
    print(f"\n🎉 FINAL SUCCESS RESULT: {result}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    db.close()