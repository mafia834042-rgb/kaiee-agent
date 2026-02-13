import os
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, Form, Depends, Request, Response
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse

# --- LOCAL IMPORTS ---
try:
    from database import get_db, engine
    from auth.models import Base
    from auth.routes import router as auth_router
    from tools.whatsapp.handler import handle_whatsapp_message
except ImportError:
    from app.database import get_db, engine
    from app.auth.models import Base
    from app.auth.routes import router as auth_router
    from app.tools.whatsapp.handler import handle_whatsapp_message

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(auth_router, prefix="/auth")

@app.get("/")
async def root():
    return {"status": "Online", "System": "Kaiee AI Agent"}

# --- 📲 WHATSAPP WEBHOOK ---
@app.post("/whatsapp")
async def whatsapp_webhook(
    # ✅ FIX: Body optional hai ("") taaki Image Only msg crash na ho
    Body: str = Form(""), 
    From: str = Form(...), 
    MediaUrl0: str = Form(None), 
    db: Session = Depends(get_db)
):
    sender_phone = From.replace("whatsapp:", "").strip()
    print(f"\n📩 Incoming from {sender_phone} (Media: {MediaUrl0})")

    # Handler Call
    try:
        response_text = await handle_whatsapp_message(Body, sender_phone, MediaUrl0, db)
    except Exception as e:
        print(f"❌ Error in Handler: {e}")
        response_text = "⚠️ Server Error. Please try again."

    # Twilio Response
    twilio_res = MessagingResponse()
    twilio_res.message(response_text)
    
    xml_output = str(twilio_res)

    # ✅ FIX: UTF-8 for Hindi/Emojis
    return Response(content=xml_output, media_type="application/xml; charset=utf-8")

if __name__ == "__main__":
    import uvicorn
    # 0.0.0.0 allow karta hai external connections ko
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)