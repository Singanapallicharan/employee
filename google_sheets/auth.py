# google_sheets/auth.py
import gspread
import re
from google.oauth2.service_account import Credentials
from datetime import datetime
from dateutil.parser import parse
from django.db import transaction
from db.models import SheetConfig, Lead, Employee, Student

def get_google_sheets_client():
    """Initialize and return authenticated Google Sheets client"""
    scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
    creds = Credentials.from_service_account_file(
        'credentials/eligo-service-account.json',
        scopes=scopes
    )
    return gspread.authorize(creds)

def get_sheet_data(sheet_id):
    """Get all data from a Google Sheet"""
    client = get_google_sheets_client()
    try:
        sheet = client.open_by_key(sheet_id).sheet1
        return sheet.get_all_values()
    except Exception as e:
        print(f"Error accessing sheet: {e}")
        return None

def normalize_header(header):
    """Normalize header names for matching"""
    if not header:
        return ""
    header = str(header).strip().lower()
    header = re.sub(r'[^a-z0-9\s]', '', header)
    header = re.sub(r'\s+', ' ', header)
    return header

def get_field_mapping(model_class):
    """Return field mapping for the specified model class"""
    if model_class.__name__ == 'Lead':
        return {
            'first name': 'first_name',
            'firstname': 'first_name',
            'fname': 'first_name',
            'given name': 'first_name',
            'forename': 'first_name',
            'first': 'first_name',
            'last name': 'last_name',
            'lastname': 'last_name',
            'lname': 'last_name',
            'surname': 'last_name',
            'family name': 'last_name',
            'last': 'last_name',
            'name': 'first_name',
            'full name': 'first_name',
            'complete name': 'first_name',
            'email': 'email',
            'email address': 'email',
            'email id': 'email',
            'e mail': 'email',
            'e-mail': 'email',
            'mail': 'email',
            'phone': 'phone',
            'phone number': 'phone',
            'contact number': 'phone',
            'mobile': 'phone',
            'mobile number': 'phone',
            'cell': 'phone',
            'cell phone': 'phone',
            'telephone': 'phone',
            'whatsapp': 'phone',
            'source': 'source',
            'lead source': 'source',
            'origin': 'source',
            'how did you hear about us': 'source',
            'referral source': 'source',
            'status': 'status',
            'lead status': 'status',
            'current status': 'status',
            'stage': 'status',
            'progress': 'status',
            'interest': 'interest',
            'interested in': 'interest',
            'product interest': 'interest',
            'service interest': 'interest',
            'looking for': 'interest',
            'requirements': 'interest',
            'notes': 'notes',
            'comments': 'notes',
            'remarks': 'notes',
            'additional information': 'notes',
            'details': 'notes'
        }
    elif model_class.__name__ == 'Employee':
        return {
            'employee id': 'employee_id',
            'emp id': 'employee_id',
            'staff id': 'employee_id',
            'employee number': 'employee_id',
            'id': 'employee_id',
            'eid': 'employee_id',
            'first name': 'first_name',
            'firstname': 'first_name',
            'fname': 'first_name',
            'given name': 'first_name',
            'forename': 'first_name',
            'first': 'first_name',
            'last name': 'last_name',
            'lastname': 'last_name',
            'lname': 'last_name',
            'surname': 'last_name',
            'family name': 'last_name',
            'last': 'last_name',
            'email': 'email',
            'email address': 'email',
            'email id': 'email',
            'e mail': 'email',
            'e-mail': 'email',
            'mail': 'email',
            'phone': 'phone',
            'phone number': 'phone',
            'contact number': 'phone',
            'mobile': 'phone',
            'mobile number': 'phone',
            'cell': 'phone',
            'cell phone': 'phone',
            'telephone': 'phone',
            'linkedin': 'linkedin_url',
            'linkedin profile': 'linkedin_url',
            'linkedin url': 'linkedin_url',
            'linkedin link': 'linkedin_url',
            'linkedin account': 'linkedin_url',
            'github': 'github_url',
            'github profile': 'github_url',
            'github url': 'github_url',
            'github link': 'github_url',
            'github account': 'github_url',
            'resume': 'resume_url',
            'cv': 'resume_url',
            'resume link': 'resume_url',
            'cv link': 'resume_url',
            'resume url': 'resume_url',
            'status': 'status',
            'employee status': 'status',
            'current status': 'status',
            'work status': 'status',
            'employment status': 'status',
            'date of birth': 'date_of_birth',
            'dob': 'date_of_birth',
            'birth date': 'date_of_birth',
            'birthday': 'date_of_birth',
            'date born': 'date_of_birth',
            'gender': 'gender',
            'nationality': 'nationality',
            'marital status': 'marital_status',
            'professional phone': 'professional_phone',
            'address': 'address',
            'pincode': 'pincode',
            'highest qualification': 'highest_qualification',
            'specialization': 'specialization',
            'institution': 'institution',
            'cgpa': 'cgpa',
            'passed out year': 'passed_out_year'
        }
    elif model_class.__name__ == 'Student':
        return {
            'student id': 'student_id',
            'student number': 'student_id',
            'roll number': 'student_id',
            'registration number': 'student_id',
            'enrollment number': 'student_id',
            'sid': 'student_id',
            'first name': 'first_name',
            'firstname': 'first_name',
            'fname': 'first_name',
            'given name': 'first_name',
            'forename': 'first_name',
            'first': 'first_name',
            'last name': 'last_name',
            'lastname': 'last_name',
            'lname': 'last_name',
            'surname': 'last_name',
            'family name': 'last_name',
            'last': 'last_name',
            'email': 'email',
            'phone': 'phone',
            'parent phone': 'parent_phone',
            'address': 'address',
            'city': 'city',
            'country': 'country',
            'department': 'department',
            'enrollment date': 'enrollment_date',
            'current semester': 'current_semester',
            'passed out year': 'passed_out_year',
            'course start date': 'course_start_date',
            'course end date': 'course_end_date',
            'high school': 'high_school',
            'high school gpa': 'high_school_gpa',
            'tuition fee': 'tuition_fee',
            'scholarship': 'scholarship',
            'scholarship details': 'scholarship_details',
            'blood group': 'blood_group',
            'allergies': 'allergies',
            'clubs': 'clubs',
            'gender': 'gender',
            'date of birth': 'date_of_birth',
            'status': 'status',
            'certificate status': 'certificate_status',
            'certificate issue date': 'certificate_issue_date'
        }
    return {}

def process_leads(headers, rows):
    """Process lead data from sheet"""
    field_mapping = get_field_mapping(Lead)
    _process_data(headers, rows, Lead, field_mapping, default_status='new')

def process_employees(headers, rows):
    """Process employee data from sheet"""
    field_mapping = get_field_mapping(Employee)
    _process_data(headers, rows, Employee, field_mapping, default_status='Applied')

def process_students(headers, rows):
    """Process student data from sheet"""
    field_mapping = get_field_mapping(Student)
    _process_data(headers, rows, Student, field_mapping, default_status='registered')

def _process_data(headers, rows, model_class, field_mapping, default_status=None):
    """Internal function to process data for all model types"""
    model_fields = {f.name for f in model_class._meta.get_fields()}
    
    with transaction.atomic():
        for row in rows:
            if not any(row):  # Skip empty rows
                continue
                
            instance_data = {}
            if default_status and 'status' in model_fields:
                instance_data['status'] = default_status
                
            # Map fields from headers to model
            for i, header in enumerate(headers):
                if i >= len(row):
                    continue
                    
                value = row[i].strip()
                if not value:
                    continue
                    
                normalized_header = normalize_header(header)
                for pattern, field_name in field_mapping.items():
                    if normalized_header == normalize_header(pattern):
                        if field_name in model_fields:
                            instance_data[field_name] = value
                            break
            
            # Handle special cases
            _handle_special_cases(instance_data, model_class)
            
            # Create/update instance
            if _is_valid_instance(instance_data, model_class):
                _create_or_update_instance(model_class, instance_data)

def _handle_special_cases(instance_data, model_class):
    """Handle special field conversions"""
    # Combined name field
    if 'first_name' not in instance_data and 'name' in instance_data:
        name_parts = instance_data['name'].split(maxsplit=1)
        instance_data['first_name'] = name_parts[0]
        if len(name_parts) > 1:
            instance_data['last_name'] = name_parts[1]
        del instance_data['name']
    
    # Date fields
    for field in list(instance_data.keys()):
        if 'date' in field.lower():
            try:
                instance_data[field] = parse(instance_data[field]).date()
            except (ValueError, TypeError):
                del instance_data[field]
    
    # Numeric fields
    numeric_fields = ['age', 'cgpa', 'tuition_fee', 'current_semester', 'passed_out_year']
    for field in numeric_fields:
        if field in instance_data:
            try:
                instance_data[field] = float(instance_data[field])
                if field in ['current_semester', 'passed_out_year']:
                    instance_data[field] = int(instance_data[field])
            except (ValueError, TypeError):
                del instance_data[field]
    
    # Boolean fields
    if 'scholarship' in instance_data:
        val = instance_data['scholarship'].lower()
        instance_data['scholarship'] = val in ('yes', 'true', '1', 'y', 't')

def _is_valid_instance(instance_data, model_class):
    """Validate if instance has required fields"""
    if model_class.__name__ == 'Lead':
        return 'email' in instance_data or 'phone' in instance_data
    elif model_class.__name__ == 'Employee':
        return 'email' in instance_data or 'employee_id' in instance_data
    elif model_class.__name__ == 'Student':
        return 'student_id' in instance_data or 'email' in instance_data
    return False

def _create_or_update_instance(model_class, instance_data):
    """Create or update database record"""
    try:
        if model_class.__name__ == 'Lead':
            lookup = {}
            if 'email' in instance_data:
                lookup['email'] = instance_data['email']
            elif 'phone' in instance_data:
                lookup['phone'] = instance_data['phone']
            
            if lookup:
                model_class.objects.update_or_create(
                    defaults=instance_data,
                    **lookup
                )
        
        elif model_class.__name__ == 'Employee':
            lookup = {}
            if 'employee_id' in instance_data:
                lookup['employee_id'] = instance_data['employee_id']
            elif 'email' in instance_data:
                lookup['email'] = instance_data['email']
            
            if lookup:
                model_class.objects.update_or_create(
                    defaults=instance_data,
                    **lookup
                )
        
        elif model_class.__name__ == 'Student':
            lookup = {}
            if 'student_id' in instance_data:
                lookup['student_id'] = instance_data['student_id']
            elif 'email' in instance_data:
                lookup['email'] = instance_data['email']
            
            if lookup:
                model_class.objects.update_or_create(
                    defaults=instance_data,
                    **lookup
                )
    
    except Exception as e:
        print(f"Error processing {model_class.__name__} instance: {e}")

def process_sheet(sheet_config):
    """Main function to process a sheet configuration"""
    data = get_sheet_data(sheet_config.sheet_id)
    if not data or len(data) < 2:  # Need headers and at least one row
        return False
        
    headers = [normalize_header(h) for h in data[0]]
    rows = data[1:]
    
    try:
        if sheet_config.sheet_type == 'LEADS':
            process_leads(headers, rows)
        elif sheet_config.sheet_type == 'EMPLOYEES':
            process_employees(headers, rows)
        elif sheet_config.sheet_type == 'STUDENTS':
            process_students(headers, rows)
        
        sheet_config.last_synced = datetime.now()
        sheet_config.save()
        return True
    except Exception as e:
        print(f"Error processing sheet: {e}")
        return False