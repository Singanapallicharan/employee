# sheets/utils/sync.py
from google_sheets.auth import get_sheet_data
from django.db import transaction
from django.utils import timezone
from db.models import SheetConfig
import logging

# Set up logging
logger = logging.getLogger(__name__)

def sync_sheet(sheet_config):
    """
    Synchronize data from Google Sheet to database based on sheet configuration
    Args:
        sheet_config (SheetConfig): The sheet configuration instance
    Returns:
        bool: True if sync succeeded, False if failed
    """
    try:
        # Get data from Google Sheets API
        data = get_sheet_data(sheet_config.sheet_id)
        if not data or len(data) < 2:  # Need headers and at least one row
            logger.warning(f"No data or insufficient rows in sheet {sheet_config.sheet_id}")
            return False

        headers = [h.strip().lower() for h in data[0]]
        rows = data[1:]

        # Process based on sheet type
        with transaction.atomic():
            if sheet_config.sheet_type == 'LEADS':
                from google_sheets.processors import process_leads
                process_leads(headers, rows)
            elif sheet_config.sheet_type == 'EMPLOYEES':
                from google_sheets.processors import process_employees
                process_employees(headers, rows)
            elif sheet_config.sheet_type == 'STUDENTS':
                from google_sheets.processors import process_students
                process_students(headers, rows)
            else:
                logger.error(f"Unknown sheet type: {sheet_config.sheet_type}")
                return False

            # Update sync status
            sheet_config.last_synced = timezone.now()
            sheet_config.save()

        logger.info(f"Successfully synced {sheet_config.sheet_type} sheet (ID: {sheet_config.sheet_id})")
        return True

    except Exception as e:
        logger.error(f"Failed to sync sheet {sheet_config.sheet_id}: {str(e)}", exc_info=True)
        return False

def sync_all_active_sheets():
    """
    Synchronize all active sheets in the system
    Returns:
        tuple: (success_count, failure_count)
    """
    active_sheets = SheetConfig.objects.filter(is_active=True)
    success_count = 0
    failure_count = 0

    for sheet in active_sheets:
        if sync_sheet(sheet):
            success_count += 1
        else:
            failure_count += 1

    logger.info(f"Sync completed. Successful: {success_count}, Failed: {failure_count}")
    return (success_count, failure_count)