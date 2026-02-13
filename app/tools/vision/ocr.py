import os
import base64
import requests
from requests.auth import HTTPBasicAuth

def analyze_bill(image_url):
    print(f"🚀 Direct API Vision Analysis: {image_url}")
    try:
        # 1. Download from Twilio
        res = requests.get(image_url, auth=HTTPBasicAuth(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")))
        if res.status_code != 200: return None, "Download Failed"
        
        image_data = base64.b64encode(res.content).decode('utf-8')
        api_key = os.getenv("GEMINI_API_KEY")

        # 🟢 FIX: Using stable 'v1' endpoint (No more 404s)
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Extract Bill Details: Item Name | Amount (Number) | Category. Format: Item | Amount | Category"},
                    {"inline_data": {"mime_type": "image/jpeg", "data": image_data}}
                ]
            }]
        }

        api_res = requests.post(url, json=payload, timeout=20)
        if api_res.status_code == 200:
            return api_res.json()['candidates'][0]['content']['parts'][0]['text'].strip(), None
        
        return None, f"API Error: {api_res.status_code}"
    except Exception as e:
        return None, str(e)