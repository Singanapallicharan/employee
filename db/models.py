from django.db import models
from datetime import date

# models.py
class SheetConfig(models.Model):
    SHEET_TYPES = [
        ('APPLICATIONS', 'Applications'),
        ('SELECTED', 'Selected Employees'),
        ('STUDENTS', 'Students'),
        ('LEADS', 'Leads')
    ]
    company = models.CharField(max_length=100)
    sheet_url = models.URLField()
    sheet_id = models.CharField(max_length=100, blank=True)  # Extracted from URL
    sheet_type = models.CharField(max_length=20, choices=SHEET_TYPES)
    last_synced_row = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Auto-extract sheet ID from URL (e.g., from https://docs.google.com/spreadsheets/d/ABC123/edit)
        if not self.sheet_id and 'spreadsheets/d/' in self.sheet_url:
            self.sheet_id = self.sheet_url.split('spreadsheets/d/')[1].split('/')[0]
        super().save(*args, **kwargs)


class Lead(models.Model):
    STATUS_CHOICES = [
        ('new', 'New'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('paid', 'not paid'),
    ]
    MONTHS = [
    ('January', 'January'),
    ('February', 'February'),
    ('March', 'March'),
    ('April', 'April'),
    ('May', 'May'),
    ('June', 'June'),
    ('July', 'July'),
    ('August', 'August'),
    ('September', 'September'),
    ('October', 'October'),
    ('November', 'November'),
    ('December', 'December'),
]

    
    name = models.CharField(blank=True,null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15,blank=True, null=True)
    whatsapp_phone = models.CharField(max_length=15,blank=True, null=True)
    college = models.CharField(max_length=100,blank=True,null=True)
    branch = models.CharField(max_length =100,blank=True,null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    current_year = models.CharField(max_length=30,blank=True,null=True)
    domain = models.CharField(max_length = 100,blank=True,null=True)  # What they're interested in
    period = models.CharField(max_length =100,blank=True,null=True)
    start_month = models.CharField(max_length = 20,choices=MONTHS,default="January")
    assigned_leads = models.CharField(
        max_length=20,
        choices=[
            ("assigned","assigned"),
            ("not assigned","not assigned"),
        ],
        default="not assigned"
    )
    created_at = models.DateTimeField(max_length =20,blank=True,null=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ===== PHASE 1 CORE FIELDS =====
    assigned_to = models.ForeignKey(
        'Employee', 
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads'
    )
    assignment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When lead was assigned to employee"
    )
    first_contact_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When employee first contacted the lead"
    )
    
    # ===== FUTURE-PROOFING FIELDS =====
    priority = models.CharField(
        max_length=10,
        choices=[
            ('high', 'High'), 
            ('medium', 'Medium'),
            ('low', 'Low')
        ],
        default='medium',
        help_text="For future priority-based assignment"
    )
    quality_score = models.PositiveSmallIntegerField(
        default=50,
        help_text="Calculated score based on profile completeness"
    )
    last_followup = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last follow-up attempt"
    )
    conversion_probability = models.FloatField(
        null=True,
        blank=True,
        help_text="AI-predicted likelihood to convert (0-1)"
    )


    def __str__(self):
        return f"{self.name} ({self.status}) - Assigned to :{self.assigned_to}"
    
from django.db import models
import uuid
from datetime import date

class Employee(models.Model):
    # Existing fields (preserved)
    employee_id = models.CharField(max_length=20, unique=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password = models.CharField(max_length=100,default="21981a05f2")
    location = models.CharField(max_length=50)
    email = models.EmailField()
    employee_type = models.CharField(
        max_length=20,
        choices=[
            ("Full Time","Full Time"),
            ("Part Time","Part Time"),
        ],
        default="Full Time"
    )
    level = models.CharField(max_length=30,default="Ps1")
    manager = models.CharField(max_length=30,default="Jay P")
    role = models.CharField(max_length=50,default="Business Development Associate")
    phone = models.CharField(max_length=15)
    linkedin_url = models.URLField(blank=True, null=True)
    github_url = models.URLField(blank=True, null=True)
    resume_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("Applied", "Applied"), 
            ("Selected", "Selected"),
            ("Active", "Active"),
            ("Inactive", "Inactive"),
            ("On Leave", "On Leave")
        ],
        default="Applied",
    )
    join_date = models.DateField(auto_now_add=True)

    applied_mail = models.CharField(
        max_length=10,
        choices = [
            ("Sent", "Sent"),
            ("Not Sent", "Not Sent"),
            ],
        default="Not Sent"
    )
    signed_mail = models.CharField(
        max_length=10,
        choices = [
            ("Sent", "Sent"),
            ("Not Sent", "Not Sent"),
            ],
        default="Not Sent"
    )
    selected_mail = models.CharField(
        max_length=10,
        choices = [
            ("Sent", "Sent"),
            ("Not Sent", "Not Sent"),
            ],
        default="Not Sent"
    )
    assigned_leads = models.CharField(
        max_length=20,
        choices = [
            ("assigned", "assigned"),
            ("Not assigned", "Not assigned"),
            ],
        default="Not assigned"
    )
    # New fields based on requirements
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True, editable=False)  # Auto-calculated
    gender = models.CharField(
        max_length=20,
        choices=[
            ("Male", "Male"),
            ("Female", "Female"),
            ("Other", "Other"),
            ("Prefer not to say", "Prefer not to say")
        ],
        blank=True,
        null=True
    )
    nationality = models.CharField(max_length=50, blank=True, null=True)
    marital_status = models.CharField(
        max_length=20,
        choices=[
            ("Single", "Single"),
            ("Married", "Married"),
            ("Divorced", "Divorced"),
            ("Widowed", "Widowed")
        ],
        blank=True,
        null=True
    )
    professional_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to='employee_profiles/',
        blank=True,
        null=True,
        help_text=".jpg format only"
    )
    highest_qualification = models.CharField(max_length=100, blank=True, null=True)
    specialization = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=150, blank=True, null=True)
    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="CGPA/Percentage"
    )
    passed_out_year = models.PositiveIntegerField(blank=True, null=True)

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        # Auto-generate employee ID if not provided
        if not self.employee_id:
            self.employee_id = f"EMP-{uuid.uuid4().hex[:8].upper()}"
        
        # Auto-calculate age if date_of_birth is provided
        if self.date_of_birth:
            today = date.today()
            self.age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Employee"
        verbose_name_plural = "Employees"
        ordering = ['-created_at']


    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.status} "

from django.db import models
from datetime import date

class Student(models.Model):
    # Status Information
    STATUS_CHOICES = [
        ('registered', 'Registered'),
        ('not_registered', 'Not Registered'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='not_registered',
        blank=True,
        null=True
    )
    
    # Personal Information
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(
        max_length=1, 
        choices=GENDER_CHOICES, 
        blank=True, 
        null=True
    )
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Contact Information
    email = models.EmailField(unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    parent_phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    
    # Academic Information
    student_id = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True, 
        null=True
    )
    department = models.CharField(max_length=50, blank=True, null=True)
    enrollment_date = models.DateField(blank=True, null=True)
    current_semester = models.PositiveSmallIntegerField(blank=True, null=True)
    passed_out_year = models.PositiveSmallIntegerField(blank=True, null=True)
    
    # Certificate Information
    CERTIFICATE_STATUS = [
        ('issued', 'Issued'),
        ('not_issued', 'Not Issued'),
    ]
    certificate_status = models.CharField(
        max_length=20,
        choices=CERTIFICATE_STATUS,
        default='not_issued',
        blank=True,
        null=True
    )
    certificate_issue_date = models.DateField(blank=True, null=True)
    
    # Course Duration
    course_start_date = models.DateField(blank=True, null=True)
    course_end_date = models.DateField(blank=True, null=True)
    
    # Additional Information
    high_school = models.CharField(max_length=100, blank=True, null=True)
    high_school_gpa = models.DecimalField(
        max_digits=3, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    tuition_fee = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        blank=True, 
        null=True
    )
    scholarship = models.BooleanField(default=False, blank=True, null=True)
    scholarship_details = models.TextField(blank=True, null=True)
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    clubs = models.TextField(blank=True, null=True)
    
    # System Information
    last_login_time = models.DateTimeField(blank=True, null=True)
    login_count = models.PositiveIntegerField(default=0, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        return f"{name} ({self.student_id or 'No ID'})"
    

from django.db import models
from django.contrib.auth import get_user_model

class CallLog(models.Model):
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE)
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=20, choices=[
        ('initiated', 'Initiated'),
        ('completed', 'Completed'),
        ('note_added', 'Note Added')
    ])
    duration = models.PositiveIntegerField(default=0)  # in seconds
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']