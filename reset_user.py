import sqlite3

conn = sqlite3.connect('kaiee.db')
cursor = conn.cursor()

try:
    # Saare users uda do (Fresh Start)
    cursor.execute("DELETE FROM users")
    print(f"✅ Success! Database se {cursor.rowcount} purane users delete kar diye.")
    conn.commit()
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()