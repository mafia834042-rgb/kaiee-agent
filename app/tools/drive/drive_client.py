# FILE: app/tools/drive/drive_client.py
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io
import os

def get_drive_service(access_token, refresh_token):
    """ Service Object banata hai using Tokens """
    creds = Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    )
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(folder_name, parent_id, service):
    """
    Folder dhundta hai. Agar nahi mila, toh naya bana deta hai.
    Returns: Folder ID
    """
    try:
        # 1. Search Query
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"
            
        results = service.files().list(q=query, fields="files(id, name)").execute()
        files = results.get('files', [])

        # 2. Agar mil gaya -> ID return karo
        if files:
            print(f"📂 Found existing folder: {folder_name}")
            return files[0]['id']
        
        # 3. Agar nahi mila -> Create karo
        print(f"✨ Creating new folder: {folder_name}")
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
            
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

    except Exception as e:
        print(f"❌ Folder Error: {e}")
        return None

def upload_bytes_to_drive(file_bytes, file_name, folder_id, user_tokens):
    """
    File Upload Function (Updated)
    """
    try:
        service = get_drive_service(
            user_tokens['access_token'], 
            user_tokens['refresh_token']
        )
        
        # File Metadata
        file_metadata = {
            'name': file_name,
        }
        # Agar Folder ID diya hai, toh usme daalo, warna Root mein
        if folder_id:
            file_metadata['parents'] = [folder_id]

        # Stream Setup
        fh = io.BytesIO(file_bytes)
        media = MediaIoBaseUpload(fh, mimetype='application/octet-stream', resumable=True)

        # Upload
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()

        return {
            "id": file.get("id"),
            "view_link": file.get("webViewLink")
        }

    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return None