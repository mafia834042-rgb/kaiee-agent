import sqlite3

# Database se connect karo
conn = sqlite3.connect('kaiee.db')
cursor = conn.cursor()

try:
    # Naya column jodo
    cursor.execute("ALTER TABLE users ADD COLUMN spreadsheet_id TEXT")
    print("✅ Success! 'spreadsheet_id' column add ho gaya.")
except sqlite3.OperationalError:
    print("⚠️ Column pehle se maujood hai. Kuch karne ki zaroorat nahi.")

conn.commit()
conn.close()