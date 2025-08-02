import gspread
import re
import os
import pickle
from django.core.management.base import BaseCommand
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from db.models import Employee

class Command(BaseCommand):
    help = 'Imports employee data from Google Sheets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--new-rows-only',
            action='store_true',
            help='Only process rows newer than last run'
        )

    def get_authenticated_client(self):
        """Handles OAuth authentication"""
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        TOKEN_FILE = 'token.pickle'

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

    def handle(self, *args, **options):
        try:
            # Initialize tracking
            LAST_ROW_FILE = 'last_row.txt'
            last_processed_row = 0
            
            # Load last processed row
            if os.path.exists(LAST_ROW_FILE):
                with open(LAST_ROW_FILE, 'r') as f:
                    last_processed_row = int(f.read().strip())

            # Connect to sheet
            gc = self.get_authenticated_client()
            sheet = gc.open_by_key("1fIJuR5AwYk-9EKim47R1yJjUyKtX1-dUBxeD-EmKfSQ").worksheet("Applications")
            all_rows = sheet.get_all_values()
            
            # Determine rows to process
            if options['new_rows_only']:
                rows = all_rows[last_processed_row + 1:]  # Only new rows
            else:
                rows = all_rows[1:]  # All rows (skip header)
                self.stdout.write("Processing all rows (full sync mode)")

            processed_count = 0
            for i, row in enumerate(rows, start=last_processed_row + 2):
                if not row[1] or not row[3]:  # Skip if no first name or email
                    continue

                data = {
                    'email': row[3].lower().strip(),
                    'defaults': {
                        'first_name': row[1].strip().title(),
                        'last_name': row[2].strip().title(),
                        'phone': re.sub(r'\D', '', row[4])[:15],
                        'linkedin_url': row[5] if row[5].startswith('http') else None,
                        'github_url': row[6] if row[6].startswith('http') else None,
                        'resume_url': row[8] if row[8] and str(row[8]).lower().endswith('.pdf') else None,
                        'status': 'Applied'
                    }
                }

                if options['dry_run']:
                    self.stdout.write(f"[DRY RUN] Row {i}: {data['email']}")
                else:
                    Employee.objects.update_or_create(**data)
                    processed_count += 1
                    if options['verbosity'] > 1:  # Only log details in verbose mode
                        self.stdout.write(self.style.SUCCESS(f"Row {i}: {data['defaults']['first_name']}"))

            # Update last processed row
            if not options['dry_run'] and not options['new_rows_only']:
                with open(LAST_ROW_FILE, 'w') as f:
                    f.write(str(len(all_rows) - 1))  # Save last row index (0-based)

            self.stdout.write(self.style.SUCCESS(
                f"Completed. Processed {processed_count} new rows. "
                f"Total rows in sheet: {len(all_rows) - 1}"
            ))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Fatal error: {str(e)}"))
            if options['verbosity'] > 0:
                import traceback
                traceback.print_exc()
            raise e