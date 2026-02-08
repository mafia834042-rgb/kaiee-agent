import datetime
from googleapiclient.discovery import build
from app.tools.drive.drive_client import get_creds_from_tokens

# --- ⚙️ CONFIGURATION: Sheet Ka Design ---
# Yahan hum define karte hain ki har Tab mein kaunse columns honge
SHEET_STRUCTURE = {
    "Expenses": [
        "Date", 
        "Item/Description", 
        "Category", 
        "Amount", 
        "Entered By", 
        "Receipt Link"
    ],
    "Sales": [
        "Date", 
        "Client Name", 
        "Product/Service", 
        "Amount", 
        "Payment Mode", 
        "Status", 
        "Entered By"
    ],
    "CRM": [
        "Date", 
        "Client Name", 
        "Phone Number", 
        "Interest Level", 
        "Notes"
    ],
    "Logs": [
        "Timestamp", 
        "User Phone", 
        "Action", 
        "Original Message"
    ]
}

def get_sheets_service(access_token, refresh_token):
    """
    Google Sheets API Service banata hai.
    """
    creds = get_creds_from_tokens(access_token, refresh_token)
    return build('sheets', 'v4', credentials=creds)

def get_drive_service_for_move(access_token, refresh_token):
    """
    Drive API Service (Sirf file move karne ke liye).
    """
    creds = get_creds_from_tokens(access_token, refresh_token)
    return build('drive', 'v3', credentials=creds)

def create_master_sheet(user, folder_id):
    """
    Magic Function jo:
    1. Nayi Sheet banata hai.
    2. 4 Tabs add karta hai (Expenses, Sales...).
    3. Headers likhta hai aur unhe BOLD + GREY karta hai.
    4. Sheet ko sahi Folder mein move karta hai.
    """
    print(f"📊 Creating Master Sheet for {user.phone_number}...")
    
    # 1. Auth Services Ready karo
    sheets_service = get_sheets_service(user.google_access_token, user.google_refresh_token)
    drive_service = get_drive_service_for_move(user.google_access_token, user.google_refresh_token)
    
    # 2. Blank Sheet Create karo
    sheet_metadata = {
        'properties': {'title': f"Kaiee_Business_Dashboard_{user.phone_number}"}
    }
    spreadsheet = sheets_service.spreadsheets().create(body=sheet_metadata, fields='spreadsheetId').execute()
    spreadsheet_id = spreadsheet.get('spreadsheetId')
    
    # 3. Tabs Banana (Batch Update)
    requests = []
    
    # Har Tab ke liye request add karo
    for title in SHEET_STRUCTURE.keys():
        requests.append({
            "addSheet": {
                "properties": {"title": title}
            }
        })
    
    # Note: Default "Sheet1" ko hum baad mein delete karenge taaki error na aaye
    
    try:
        # Tabs banao
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, 
            body={"requests": requests}
        ).execute()
        
        # Ab Default "Sheet1" (ID:0) ko delete kar do (Safayi)
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, 
            body={"requests": [{"deleteSheet": {"sheetId": 0}}]}
        ).execute()
        
    except Exception as e:
        print(f"⚠️ Tab creation note: {e}")

    # 4. Headers & Formatting (Bold + Grey Background)
    # Pehle naye Sheet IDs nikalo taaki hume pata ho kahan likhna hai
    sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    sheets_info = {s['properties']['title']: s['properties']['sheetId'] for s in sheet_metadata['sheets']}
    
    header_requests = []
    
    for title, headers in SHEET_STRUCTURE.items():
        if title in sheets_info:
            # Har header cell ke liye formatting prepare karo
            header_cells = []
            for h in headers:
                header_cells.append({
                    "userEnteredValue": {"stringValue": h},
                    "userEnteredFormat": {
                        # BOLD Text
                        "textFormat": {"bold": True},
                        # LIGHT GREY Background (Professional Look)
                        "backgroundColor": {"red": 0.9, "green": 0.9, "blue": 0.9} 
                    }
                })

            # Pura Row Update karne ka request
            header_requests.append({
                "updateCells": {
                    "start": {
                        "sheetId": sheets_info[title], 
                        "rowIndex": 0, 
                        "columnIndex": 0
                    },
                    "rows": [{"values": header_cells}],
                    "fields": "userEnteredValue,userEnteredFormat"
                }
            })
            
    if header_requests:
        sheets_service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id, 
            body={"requests": header_requests}
        ).execute()

    # 5. Move File to 'Kaiee_Team_Data' Folder
    # By default root me banti hai, usse utha ke folder me daalo
    file = drive_service.files().get(fileId=spreadsheet_id, fields='parents').execute()
    previous_parents = ",".join(file.get('parents'))
    
    if folder_id:
        drive_service.files().update(
            fileId=spreadsheet_id,
            addParents=folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
    
    return spreadsheet_id

def append_row_to_sheet(user, spreadsheet_id, tab_name, row_data):
    """
    Existing Sheet ke neeche naya data add karta hai.
    Example: Expenses tab mein nayi entry.
    """
    service = get_sheets_service(user.google_access_token, user.google_refresh_token)
    
    # Range: e.g., "Expenses!A:Z" (Matlab A se Z tak kahin bhi likho)
    range_name = f"{tab_name}!A:Z"
    body = {"values": [row_data]}
    
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()
    
    return result