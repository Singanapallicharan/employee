from django import forms
from .models import Employee, Student, Lead

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = '__all__'  # Or list specific fields
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'join_date': forms.DateInput(attrs={'type': 'date'}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = '__all__'

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = '__all__'

# forms.py
from django import forms
from .models import SheetConfig

class SheetConfigForm(forms.ModelForm):
    class Meta:
        model = SheetConfig
        fields = ['sheet_url', 'sheet_type']
        widgets = {
            'sheet_url': forms.URLInput(attrs={
                'placeholder': 'https://docs.google.com/spreadsheets/d/...',
                'class': 'form-control'
            }),
            'sheet_type': forms.Select(attrs={'class': 'form-control'})
        }

# myapp/forms.py
from django import forms

SHEET_TYPE_CHOICES = [
    ('LEADS', 'Leads'),
    ('EMPLOYEES', 'Employees'),
    ('STUDENTS', 'Students'),
]

class SheetConfigForm(forms.Form):
    company = forms.CharField(
        label='Company',
        max_length=100,  # Added max_length
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter your company name',  # Fixed typo
            'class': 'form-control'
        })
    )
    
    sheet_url = forms.URLField(
        label='Google Sheet URL',
        widget=forms.URLInput(attrs={
            'placeholder': 'https://docs.google.com/spreadsheets/d/...',
            'class': 'form-control'
        })
    )
    
    sheet_type = forms.ChoiceField(
        label='Sheet Type',
        choices=SHEET_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )