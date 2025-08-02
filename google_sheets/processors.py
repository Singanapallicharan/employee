# google_sheets/processors.py
from django.db import transaction
from dateutil.parser import parse
from db.models import Lead, Employee, Student
from .auth import get_field_mapping, normalize_header
import logging

logger = logging.getLogger(__name__)

def _process_data(headers, rows, model_class, field_mapping, default_status):
    """Core data processing logic"""
    model_fields = {f.name for f in model_class._meta.get_fields()}
    created = updated = 0
    
    with transaction.atomic():
        for row_idx, row in enumerate(rows, start=2):  # Rows start at 2 (header is 1)
            try:
                if not any(row):  # Skip empty rows
                    continue
                    
                instance_data = {}
                if default_status and 'status' in model_fields:
                    instance_data['status'] = default_status
                
                # Map fields from spreadsheet to model
                for col_idx, header in enumerate(headers):
                    if col_idx >= len(row):
                        continue
                        
                    value = str(row[col_idx]).strip()
                    if not value:
                        continue
                        
                    normalized_header = normalize_header(header)
                    for pattern, field_name in field_mapping.items():
                        if normalize_header(pattern) == normalized_header:
                            if field_name in model_fields:
                                instance_data[field_name] = value
                                break
                
                # Process special fields
                instance_data = _transform_fields(instance_data, model_class)
                
                # Create/update record
                if _is_valid_instance(instance_data, model_class):
                    obj, created_flag = _save_instance(model_class, instance_data)
                    if created_flag:
                        created += 1
                    else:
                        updated += 1
                        
            except Exception as e:
                logger.error(f"Error processing row {row_idx}: {str(e)}")
                continue
                
        logger.info(f"Processed {len(rows)} rows. Created: {created}, Updated: {updated}")

def _transform_fields(data, model_class):
    """Convert field values to appropriate types"""
    # Date fields
    for field in list(data.keys()):
        if 'date' in field.lower():
            try:
                data[field] = parse(data[field]).date()
            except (ValueError, TypeError):
                del data[field]
    
    # Numeric fields
    numeric_fields = ['age', 'cgpa', 'tuition_fee', 'current_semester', 'passed_out_year']
    for field in numeric_fields:
        if field in data:
            try:
                data[field] = float(data[field])
                if field in ['current_semester', 'passed_out_year']:
                    data[field] = int(data[field])
            except (ValueError, TypeError):
                del data[field]
    
    # Boolean fields
    if 'scholarship' in data:
        val = data['scholarship'].lower()
        data['scholarship'] = val in ('yes', 'true', '1', 'y', 't')
    
    return data

def _is_valid_instance(data, model_class):
    """Validate required fields"""
    if model_class.__name__ == 'Lead':
        return 'email' in data or 'phone' in data
    elif model_class.__name__ == 'Employee':
        return 'email' in data or 'employee_id' in data
    elif model_class.__name__ == 'Student':
        return 'student_id' in data or 'email' in data
    return False

def _save_instance(model_class, data):
    """Save instance to database"""
    lookup = {}
    if model_class.__name__ == 'Lead':
        if 'email' in data:
            lookup['email'] = data['email']
        elif 'phone' in data:
            lookup['phone'] = data['phone']
    elif model_class.__name__ == 'Employee':
        if 'employee_id' in data:
            lookup['employee_id'] = data['employee_id']
        elif 'email' in data:
            lookup['email'] = data['email']
    elif model_class.__name__ == 'Student':
        if 'student_id' in data:
            lookup['student_id'] = data['student_id']
        elif 'email' in data:
            lookup['email'] = data['email']
    
    if lookup:
        return model_class.objects.update_or_create(
            defaults=data,
            **lookup
        )
    return (None, False)