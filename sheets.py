import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import get_as_dataframe
from datetime import datetime
import django
import os
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eligodb.settings")
django.setup()

from db.models import Employee

# Define scope and authorize credentials
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open Google Sheet
sheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1fIJuR5AwYk-9EKim47R1yJjUyKtX1-dUBxeD-EmKfSQ/edit#gid=0")
worksheet = sheet.worksheet("Applications")

# Read sheet into DataFrame
data = worksheet.get_all_records()
df = pd.DataFrame(data)

# Iterate and insert into model
for _, row in df.iterrows():
    try:
        employee, created = Employee.objects.get_or_create(
            email=row.get("Email").strip(),
            defaults={
                "first_name": row.get("First name", "").strip(),
                "last_name": row.get("Last name", "").strip(),
                "phone": str(row.get("Phone", "")).strip(),
                "linkedin_url": row.get("LinkedIn", "").strip() or None,
                "github_url": row.get("Github", "").strip() or None,
                "resume_url": row.get("Resume", "").strip() or None,
                "status": "Applied",
                "location": "",  # You can update if location exists in sheet
                "join_date": datetime.strptime(row.get("Date and time", ""), "%m/%d/%Y %H:%M:%S").date() if row.get("Date and time") else None,
            }
        )
        if created:
            print(f"Inserted: {employee.first_name} {employee.last_name}")
        else:
            print(f"Skipped (Already Exists): {employee.first_name} {employee.last_name}")
    except Exception as e:
        print(f"Error processing row {row}: {e}")
