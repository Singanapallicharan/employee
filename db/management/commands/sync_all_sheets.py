# management/commands/sync_all_sheets.py
from django.core.management.base import BaseCommand
from utils.sync import sync_all_active_sheets

class Command(BaseCommand):
    help = 'Sync all active Google Sheets'

    def handle(self, *args, **options):
        success, failures = sync_all_active_sheets()
        self.stdout.write(self.style.SUCCESS(f'Synced {success} sheets successfully'))
        if failures:
            self.stdout.write(self.style.ERROR(f'Failed to sync {failures} sheets'))