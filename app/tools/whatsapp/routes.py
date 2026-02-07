# FILE: app/tools/whatsapp/routes.py
from fastapi import APIRouter, Request, Depends, Form, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.tools.whatsapp.handler import handle_whatsapp_message

router = APIRouter()

@router.post("/whatsapp")
async def whatsapp_webhook(
    Body: str = Form(default=""),
    From: str = Form(...),
    MediaUrl0: str = Form(default=None),
    db: Session = Depends(get_db)
):
    # --- FIX: Pehle sirf "whatsapp:" hata rahe the, ab "+" bhi hatayenge ---
    sender_phone = From.replace("whatsapp:", "").replace("+", "").strip()
    
    # Ab sender_phone hamesha "918340..." hoga (No + symbol)
    
    response_text = await handle_whatsapp_message(
        message_body=Body,
        sender_phone=sender_phone,
        media_url=MediaUrl0,
        db=db
    )
    
    # XML Response
    xml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
    <Response>
        <Message>{response_text}</Message>
    </Response>"""
    
    return Response(content=xml_response, media_type="application/xml")