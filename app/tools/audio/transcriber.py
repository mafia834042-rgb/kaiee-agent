import os
import requests
from groq import Groq
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv  # <-- NEW: Import this

# 0. Sabse pehle Keys Load karo!
load_dotenv()

# 1. Groq Client Setup (Free & Fast)
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("⚠️ WARNING: Groq API Key nahi mili! Audio kaam nahi karega.")
    client = None
else:
    client = Groq(api_key=api_key)

def transcribe_audio(media_url):
    """
    WhatsApp Audio URL -> Text (Hindi/English)
    """
    if not client:
        return None, "❌ Server Error: AI Key Missing"

    print(f"🎤 Downloading Audio from: {media_url}")
    
    # 2. Audio Download from Twilio
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    
    try:
        response = requests.get(media_url, auth=HTTPBasicAuth(account_sid, auth_token))
        if response.status_code != 200:
            return None, "❌ Audio Download Failed"
            
        # Temp file save karo
        filename = f"temp_{os.urandom(4).hex()}.ogg"
        with open(filename, "wb") as f:
            f.write(response.content)
            
        # 3. Groq AI Magic (Speech to Text)
        with open(filename, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(filename, file.read()),
                model="whisper-large-v3",
                prompt="User is speaking Hinglish. Business expense related.",
                response_format="text"
            )
        
        # Cleanup (Delete temp file)
        if os.path.exists(filename):
            os.remove(filename)
        
        text = transcription.strip()
        print(f"🗣️ Transcribed Text: {text}")
        return text, None

    except Exception as e:
        print(f"❌ Audio Error: {e}")
        # Cleanup on error
        if 'filename' in locals() and os.path.exists(filename):
            os.remove(filename)
        return None, str(e)