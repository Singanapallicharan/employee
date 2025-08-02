import os
import time
import gspread
import pickle
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from django.core.management import call_command

# OAuth Config
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
TOKEN_FILE = 'token.pickle'
SHEET_ID = '1fIJuR5AwYk-9EKim47R1yJjUyKtX1-dUBxeD-EmKfSQ'  # Your sheet ID
CHECK_INTERVAL = 300  # 5 minutes

def get_authenticated_client():
    """Handles OAuth authentication with token refresh"""
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'oauth_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return gspread.authorize(creds)

def check_for_updates():
    """Checks for new rows and processes them"""
    gc = get_authenticated_client()
    sheet = gc.open_by_key(SHEET_ID).worksheet("Applications")
    rows = sheet.get_all_values()
    
    # Get last processed row (stored in a file)
    last_row = 0
    if os.path.exists('last_row.txt'):
        with open('last_row.txt', 'r') as f:
            last_row = int(f.read().strip())

    new_rows = rows[last_row + 1:]  # Get only new rows
    
    if new_rows:
        # Process new rows via your existing management command
        call_command('import_employees', new_rows_only=True)
        
        # Update last processed row
        with open('last_row.txt', 'w') as f:
            f.write(str(len(rows)))

if __name__ == "__main__":
    while True:
        check_for_updates()
        time.sleep(CHECK_INTERVAL)  # Check every 5 minutes