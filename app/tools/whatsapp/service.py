import requests
import uuid
import os

def download_whatsapp_media(media_url: str, auth: tuple) -> str:
    r = requests.get(media_url, auth=auth)
    r.raise_for_status()

    ext = ".bin"
    content_type = r.headers.get("Content-Type", "")
    if "image" in content_type:
        ext = ".jpg"
    elif "pdf" in content_type:
        ext = ".pdf"

    filename = f"/tmp/{uuid.uuid4()}{ext}"
    with open(filename, "wb") as f:
        f.write(r.content)

    return filename