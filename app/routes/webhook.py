from fastapi.responses import Response
from fastapi import APIRouter, Request, Depends
from sqlalchemy.orm import Session
from twilio.twiml.messaging_response import MessagingResponse
from app.db.database import get_db
from app.tools.whatsapp.handler import handle_whatsapp_message

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    
    message_body = form.get("Body")
    sender = form.get("From")
    media_url = form.get("MediaUrl0")

    reply_text = await handle_whatsapp_message(
        message_body,
        sender,
        media_url,
        db
    )

    # ✅ Twilio proper XML response
    resp = MessagingResponse()
    resp.message(reply_text)

    return Response(
        content=str(resp),
        media_type="application/xml"
    )