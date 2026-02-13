import os
import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

# --- 1. Service Helper (Connection) ---
def get_sheets_service(user):
    creds = Credentials(
        token=user.google_access_token,
        refresh_token=user.google_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET")
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build('sheets', 'v4', credentials=creds)

# --- 2. Create Sheet (THE MISSING LOGIC) ---
def create_master_sheet(user, folder_id):
    try:
        service = get_sheets_service(user)
        
        # Sheet ka structure define karo
        spreadsheet_body = {
            'properties': {'title': 'Kaiee_Business_Data'},
            'sheets': [
                {'properties': {'title': 'Expenses'}},
                {'properties': {'title': 'Sales'}}
            ]
        }
        
        # Google Drive Folder mein sheet banana thoda tricky hota hai,
        # isliye pehle sheet banate hain, fir move karte hain.
        # Simple tareeka: Bas create karo, ID return karo.
        
        spreadsheet = service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
        sheet_id = spreadsheet.get('spreadsheetId')
        
        # Headers Daalo
        headers = [["Date", "Item", "Category", "Amount", "Entered By", "Proof/Link"]]
        sales_headers = [["Date", "Customer", "Item", "Amount", "Mode", "Status", "By"]]
        
        append_row_to_sheet(user, sheet_id, "Expenses", headers[0])
        append_row_to_sheet(user, sheet_id, "Sales", sales_headers[0])
        
        print(f"📄 Sheet Created Successfully with ID: {sheet_id}")
        return sheet_id  # 👈 YE RETURN STATEMENT BAHUT ZAROORI HAI

    except Exception as e:
        print(f"❌ Error creating sheet: {e}")
        return None

# --- 3. Write Data (Likho) ---
def append_row_to_sheet(user, spreadsheet_id, sheet_name, row_values):
    try:
        service = get_sheets_service(user)
        body = {'values': [row_values]}
        service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f"{sheet_name}!A1",
            valueInputOption="USER_ENTERED",
            body=body
        ).execute()
        return True
    except Exception as e:
        print(f"❌ Write Error: {e}")
        return False

# --- 4. Read Data (Padho) ---
def get_sheet_data(user, spreadsheet_id, sheet_name):
    try:
        service = get_sheets_service(user)
        range_name = f"{sheet_name}!A:G"
        result = service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute()
        return result.get('values', [])
    except Exception as e:
        print(f"❌ Read Error: {e}")
        return []