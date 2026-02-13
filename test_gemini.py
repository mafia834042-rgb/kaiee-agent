import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY").strip()

# Hum in 3 models ko check karenge
models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-001",
    "gemini-1.5-pro",
    "gemini-1.0-pro"
]

print(f"🔑 Testing API Key: {api_key[:5]}...******")

for model in models_to_test:
    print(f"\n🔍 Testing Model: {model}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    payload = {"contents": [{"parts": [{"text": "Hi"}]}]}
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            print(f"✅ SUCCESS! Model '{model}' chal raha hai!")
            print(f"👉 Is naam ko handler.py mein use karein.")
            break
        else:
            print(f"❌ Failed ({response.status_code}): {response.text[:100]}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")

print("\n--------------------------------")
print("Agar saare fail huye, toh shayad API Key mein issue hai.")