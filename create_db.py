# FILE: create_db.py
from app.db.session import engine, Base
from app.auth.models import User

print("🔄 Creating Database Tables...")
try:
    # Ye line magic karegi: Saare models ki tables bana degi
    Base.metadata.create_all(bind=engine)
    print("✅ Success! 'users' table ban gayi hai.")
except Exception as e:
    print(f"❌ Error: {e}")