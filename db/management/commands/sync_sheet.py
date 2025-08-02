# your_app/management/commands/sync_sheet.py
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from db.models import SheetConfig  # Import your SheetConfig model
from utils.sync import sync_sheet  # Import your sync function
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Synchronizes data from a specific Google Sheet to the database'

    def add_arguments(self, parser):
        parser.add_argument(
            'sheet_id',
            type=int,
            help='ID of the SheetConfig to synchronize'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force sync even if sheet is marked inactive'
        )

    def handle(self, *args, **options):
        try:
            sheet_id = options['sheet_id']
            force = options['force']
            
            # Get the sheet configuration
            try:
                sheet = SheetConfig.objects.get(id=sheet_id)
            except SheetConfig.DoesNotExist:
                raise CommandError(f"SheetConfig with ID {sheet_id} does not exist")
            
            # Check if sheet is active (unless forced)
            if not sheet.is_active and not force:
                raise CommandError(
                    f"Sheet {sheet_id} is not active. Use --force to sync anyway."
                )
            
            # Perform the sync
            self.stdout.write(f"Starting sync for sheet ID {sheet_id}...")
            start_time = timezone.now()
            
            if sync_sheet(sheet):
                duration = timezone.now() - start_time
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Successfully synced sheet '{sheet.sheet_type}' (ID: {sheet_id}) in {duration.total_seconds():.2f} seconds"
                    )
                )
            else:
                raise CommandError(f"Failed to sync sheet ID {sheet_id}")
                
        except Exception as e:
            logger.error(f"Error in sync_sheet command: {str(e)}", exc_info=True)
            raise CommandError(str(e))