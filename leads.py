import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import django
import os
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eligodb.settings")
django.setup()

from db.models import Lead

# Define scope and authorize credentials
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1qXWelSBp5QEb0E6qRgOTYsu68tU-T5p_RHeKTRwJg64/edit?gid=0#gid=0")
worksheet = sheet.worksheet("Leads")

# Read sheet into DataFrame
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Month mapping for start_month field
MONTH_MAPPING = {
    'jan': 'January', 'feb': 'February', 'mar': 'March', 'apr': 'April',
    'may': 'May', 'jun': 'June', 'jul': 'July', 'aug': 'August',
    'sep': 'September', 'oct': 'October', 'nov': 'November', 'dec': 'December'
}

def extract_month(month_str):
    if not month_str or pd.isna(month_str):
        return "January"
    
    month_str = str(month_str).strip().lower()[:3]
    return MONTH_MAPPING.get(month_str, "January")

# Iterate and insert into model
for _, row in df.iterrows():
    try:
        lead, created = Lead.objects.get_or_create(
            email=str(row.get("E-mail ID", "")).strip(),
            defaults={
                "name": str(row.get("Name", "")).strip(),
                "phone": str(row.get("Contact Number", "")).strip(),
                "whatsapp_phone": str(row.get("Whatsapp Number", "")).strip(),
                "college": str(row.get("College Name", "")).strip(),
                "branch": str(row.get("Branch", "")).strip(),
                "current_year": str(row.get("Current Year of Srudy", "")).strip(),
                "domain": str(row.get("Domains", "")).strip(),
                "period": str(row.get("Internship Period", "")).strip(),
                "start_month": extract_month(row.get("From which month you want to start your Training+Internship program?")),
                "status": "paid" if str(row.get("Column", "")).strip().lower() == "paid" else "new",
                "created_at": datetime.strptime(row["Timestamp"], "%m/%d/%Y %H:%M:%S") if pd.notna(row.get("Timestamp")) else datetime.now(),
            }
        )
        if created:
            print(f"✅ Inserted: {lead.name} ({lead.email})")
        else:
            print(f"⏩ Skipped (Exists): {lead.name} ({lead.email})")
    except Exception as e:
        print(f"❌ Error processing row: {e}")
        print(f"Problematic row data: {dict(row)}")