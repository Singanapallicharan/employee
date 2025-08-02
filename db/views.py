from django.shortcuts import render
from .models import Employee,Student,Lead
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
import json
from django.db.models import Q


def home(request):
    return render(request, 'base.html')

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
import json
from .models import Employee

# views.py
@require_GET
def search(request):
    try:
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'results': [], 'count': 0})

        results = []
        
        # Search employees
        employees = Employee.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
       )[:5]
        
        
        for emp in employees:
         results.append({
            'type': 'Employee',
            'subtype': emp.status.capitalize(),  # Applied, Selected, Active, Inactive
            'name': f"{emp.first_name} {emp.last_name}",
            'detail': emp.email,
            'url': f"#employee-{emp.status.lower()}",  # Will trigger navigation
            'image': emp.profile_image.url if hasattr(emp, 'profile_image') else None,
            'id': emp.id
        })
        
        # Search students
        students = Student.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query) |
        Q(student_id__icontains=query)
       )[:5]
    
        for student in students:
           results.append({
            'type': 'Student',
            'subtype': student.status.replace('_', ' ').capitalize(),  # Registered, Not registered, Completed
            'name': f"{student.first_name} {student.last_name}",
            'detail': student.student_id,
            'url': f"#student-{student.status.lower().replace('_', '-')}",  # Will trigger navigation
            'image': student.profile_image.url if hasattr(student, 'profile_image') else None,
            'id': student.id
        })
           
           # Search leads
        leads = Lead.objects.filter(
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(phone__icontains=query)
       )[:5]
    
        for lead in leads:
         results.append({
            'type': 'Lead',
            'subtype': lead.status.replace('_', ' ').capitalize(),  # New, Interested, Not interested
            'name': f"{lead.first_name} {lead.last_name}",
            'detail': lead.status,
            'url': f"#lead-{lead.status.lower().replace('_', '-')}",  # Will trigger navigation
            'image': None,
            'id': lead.id
        })
        
        return JsonResponse({
            'success': True,
            'count': len(results),
            'results': results
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@require_GET
def get_applied_employees(request):
    try:
        employees = Employee.objects.filter(status__iexact='applied')
        data = [{
            'id': emp.id,
            'employee_id': emp.employee_id,
            'name': f"{emp.first_name} {emp.last_name}",
            'email': emp.email,
            'phone': emp.phone,
            'status': emp.status.lower(),
            'join_date': emp.join_date.strftime('%Y-%m-%d') if emp.join_date else None
        } for emp in employees]
        
        return JsonResponse({
            'success': True,
            'count': len(data),
            'employees': data
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

@csrf_exempt
@require_POST
def add_employee(request):
    try:
        data = json.loads(request.body)
        
        # Required fields validation
        required_fields = ['employee_id', 'first_name', 'last_name', 'email', 'phone', 'status']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)

        # Check for duplicates
        if Employee.objects.filter(employee_id=data['employee_id']).exists():
            return JsonResponse({
                'success': False,
                'error': 'Employee ID already exists'
            }, status=400)

        # Create employee
        emp = Employee.objects.create(
            employee_id=data['employee_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            status=data['status'],
            gender=data.get('gender', 'O'),
            location=data.get('location', ''),
            join_date=data.get('join_date') or date.today()
        )

        return JsonResponse({
            'success': True,
            'id': emp.id,
            'employee_id': emp.employee_id
        })

    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

@csrf_exempt
@require_http_methods(["POST"])
@csrf_exempt
@require_POST
def update_status(request, emp_id):
    try:
        data = json.loads(request.body)
        emp = get_object_or_404(Employee, id=emp_id)
        
        valid_statuses = ['applied', 'selected', 'active', 'inactive']
        if 'status' not in data or data['status'].lower() not in valid_statuses:
            return JsonResponse({'error': 'Invalid status'}, status=400)
            
        emp.status = data['status'].lower()
        emp.save()
        return JsonResponse({'success': True, 'new_status': emp.status})
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@csrf_exempt
def delete_employee(request, emp_id):
    emp = get_object_or_404(Employee, id=emp_id)
    emp.delete()
    return JsonResponse({'success': True})

# In views.py
def get_selected_employees(request):
    employees = Employee.objects.filter(status__iexact='selected')  # Case-insensitive
    data = [
        {
            'id': emp.id,
            'employee_id': emp.employee_id,
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'gender': emp.gender,
            'phone': emp.phone,
            'location': emp.location,
            'email': emp.email,
            'join_date': emp.join_date.strftime("%Y-%m-%d") if emp.join_date else '',
            'status': emp.status
        }
        for emp in employees
    ]
    return JsonResponse({'employees': data})

from django.http import JsonResponse

def get_active_employees(request):
    employees = Employee.objects.filter(status__iexact='active')
    data = [
        {
            'id': emp.id,
            'employee_id': emp.employee_id,
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'gender': emp.gender,
            'phone': emp.phone,
            'location': emp.location,
            'email': emp.email,
            'join_date': emp.join_date.strftime('%Y-%m-%d') if emp.join_date else '',
            'status': emp.status.lower(),  # Ensure consistent case
        }
        for emp in employees
    ]
    return JsonResponse({'employees': data})

def get_inactive_employees(request):
    employees = Employee.objects.filter(status__iexact='inactive')
    data = [
        {
            'id': emp.id,
            'employee_id': emp.employee_id,
            'first_name': emp.first_name,
            'last_name': emp.last_name,
            'gender': emp.gender,
            'phone': emp.phone,
            'location': emp.location,
            'email': emp.email,
            'join_date': emp.join_date.strftime('%Y-%m-%d') if emp.join_date else '',
            'status': emp.status.lower(),  # Ensure consistent case
        }
        for emp in employees
    ]
    return JsonResponse({'employees': data})

from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Student
from django.core.paginator import Paginator


def get_registered_students(request):
    try:
        students = Student.objects.filter(status__iexact='registered')
        
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'student_id': student.student_id or '',
                'name': f"{student.first_name or ''} {student.last_name or ''}".strip(),
                'gender': student.get_gender_display() if student.gender else '',
                'email': student.email or '',
                'phone': student.phone or '',
                'location': f"{student.city or ''}, {student.country or ''}".strip(', '),
                'department': student.department or '',
                'enrollment_date': student.enrollment_date.strftime('%Y-%m-%d') if student.enrollment_date else '',
                'certificate_status': student.get_certificate_status_display() if student.certificate_status else '',
                'course_start_date': student.course_start_date.strftime('%Y-%m-%d') if student.course_start_date else '',
                'course_end_date': student.course_end_date.strftime('%Y-%m-%d') if student.course_end_date else '',
                'passed_out_year': student.passed_out_year or '',
                'last_login': student.last_login_time.strftime('%Y-%m-%d %H:%M') if student.last_login_time else 'Never',
                'status': student.status or '',
                'login_count': student.login_count or 0
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    

from django.views.decorators.http import require_POST

from datetime import date  # Add this import at the top of views.py

@csrf_exempt
@require_POST
def add_student(request):
    try:
        data = json.loads(request.body)
        print("Received data:", data)  # Debug logging

        # Required fields validation
        required_fields = ['student_id', 'first_name', 'last_name', 'email', 'phone']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)

        # Check for duplicates
        if Student.objects.filter(student_id=data['student_id']).exists():
            return JsonResponse({
                'success': False, 
                'error': 'Student ID already exists'
            }, status=400)

        if Student.objects.filter(email=data['email']).exists():
            return JsonResponse({
                'success': False,
                'error': 'Email already exists'
            }, status=400)

        # Handle date fields
        enrollment_date = data.get('enrollment_date')
        if enrollment_date:
            try:
                enrollment_date = date.fromisoformat(enrollment_date)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid enrollment_date format. Use YYYY-MM-DD'
                }, status=400)
        else:
            enrollment_date = date.today()

        # Create student
        student = Student.objects.create(
            student_id=data['student_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            gender=data.get('gender', 'O'),
            city=data.get('city', ''),
            country=data.get('country', ''),
            department=data.get('department', ''),
            enrollment_date=enrollment_date,
            status=data.get('status', 'registered'),
            certificate_status=data.get('certificate_status', 'not_issued')
        )

        return JsonResponse({
            'success': True,
            'student_id': student.id,
            'message': 'Student created successfully'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
# views.py
@csrf_exempt
@require_POST
def update_student_status(request, student_id):
    try:
        data = json.loads(request.body)
        student = get_object_or_404(Student, id=student_id)
        
        if 'status' not in data:
            return JsonResponse({'success': False, 'error': 'Status field is required'}, status=400)
        
        student.status = data['status']
        student.save()
        
        return JsonResponse({
            'success': True,
            'student_id': student.id,
            'new_status': student.status
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    
# views.py
@csrf_exempt
@require_http_methods(["POST"])
def delete_student(request, student_id):
    try:
        student = get_object_or_404(Student, id=student_id)
        student.delete()
        return JsonResponse({
            'success': True,
            'message': f'Student {student_id} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
# views.py
@require_GET
def get_not_registered_students(request):
    try:
        students = Student.objects.filter(status='not_registered').order_by('-created_at')
        
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'student_id': student.student_id or '',
                'name': f"{student.first_name or ''} {student.last_name or ''}".strip(),
                'gender': student.get_gender_display() if student.gender else '',
                'email': student.email or '',
                'phone': student.phone or '',
                'location': f"{student.city or ''}, {student.country or ''}".strip(', '),
                'department': student.department or '',
                'created_at': student.created_at.strftime('%Y-%m-%d %H:%M') if student.created_at else '',
                'status': student.status or ''
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# views.py
@require_GET
def get_completed_students(request):
    try:
        students = Student.objects.filter(status='completed').order_by('-course_end_date')
        
        students_data = []
        for student in students:
            students_data.append({
                'id': student.id,
                'student_id': student.student_id or '',
                'name': f"{student.first_name or ''} {student.last_name or ''}".strip(),
                'gender': student.get_gender_display() if student.gender else '',
                'email': student.email or '',
                'phone': student.phone or '',
                'location': f"{student.city or ''}, {student.country or ''}".strip(', '),
                'department': student.department or '',
                'course_start_date': student.course_start_date.strftime('%Y-%m-%d') if student.course_start_date else '',
                'course_end_date': student.course_end_date.strftime('%Y-%m-%d') if student.course_end_date else '',
                'passed_out_year': student.passed_out_year or '',
                'certificate_status': student.get_certificate_status_display() if student.certificate_status else '',
                'certificate_issue_date': student.certificate_issue_date.strftime('%Y-%m-%d') if student.certificate_issue_date else '',
                'status': student.status or ''
            })
        
        return JsonResponse({
            'success': True,
            'students': students_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
# views.py

def get_new_leads(request):
    try:
        leads = Lead.objects.filter(status='new').order_by('-created_at')
        
        leads_data = []
        for lead in leads:
            leads_data.append({
                'id': lead.id,
                'name': lead.name,
                'email': lead.email,
                'phone': lead.phone,
                'college': lead.college,
                'current_year': lead.current_year,
                'created_at': lead.created_at.strftime('%Y-%m-%d %H:%M'),
                'status': lead.status
            })
        
        return JsonResponse({
            'success': True,
            'leads': leads_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
# views.py
@csrf_exempt
@require_POST
def add_lead(request):
    try:
        data = json.loads(request.body)
        
        # Required fields validation
        required_fields = ['first_name', 'last_name', 'email', 'phone', 'source']
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return JsonResponse({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)

        lead = Lead.objects.create(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            phone=data['phone'],
            source=data['source'],
            interest=data.get('interest', ''),
            status=data.get('status', 'new')
        )

        return JsonResponse({
            'success': True,
            'lead_id': lead.id,
            'message': 'Lead created successfully'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_POST
def update_lead_status(request, lead_id):
    try:
        data = json.loads(request.body)
        lead = get_object_or_404(Lead, id=lead_id)
        
        if 'status' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Status field is required'
            }, status=400)
        
        lead.status = data['status']
        lead.save()
        
        return JsonResponse({
            'success': True,
            'lead_id': lead.id,
            'new_status': lead.status
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@csrf_exempt
@require_POST
def delete_lead(request, lead_id):
    try:
        lead = get_object_or_404(Lead, id=lead_id)
        lead.delete()
        return JsonResponse({
            'success': True,
            'message': f'Lead {lead_id} deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
    # views.py
@require_GET
def get_interested_leads(request):
    try:
        leads = Lead.objects.filter(status='interested').order_by('-updated_at')
        
        leads_data = []
        for lead in leads:
            leads_data.append({
                'id': lead.id,
                'name': f"{lead.first_name or ''} {lead.last_name or ''}".strip(),
                'email': lead.email or '',
                'phone': lead.phone or '',
                'source': lead.source or '',
                'interest': lead.interest or '',
                'notes': lead.notes or '',
                'created_at': lead.created_at.strftime('%Y-%m-%d %H:%M') if lead.created_at else '',
                'updated_at': lead.updated_at.strftime('%Y-%m-%d %H:%M') if lead.updated_at else '',
                'status': lead.status
            })
        
        return JsonResponse({
            'success': True,
            'leads': leads_data,
            'count': len(leads_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
# views.py
@csrf_exempt
@require_POST
def add_lead_note(request, lead_id):
    try:
        data = json.loads(request.body)
        lead = get_object_or_404(Lead, id=lead_id)
        
        if 'note' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Note field is required'
            }, status=400)
        
        if lead.notes:
            lead.notes += f"\n{data['note']}"
        else:
            lead.notes = data['note']
        
        lead.save()
        
        return JsonResponse({
            'success': True,
            'lead_id': lead.id,
            'message': 'Note added successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
# views.py
@require_GET
def get_not_interested_leads(request):
    try:
        leads = Lead.objects.filter(status='not_interested').order_by('-updated_at')
        
        leads_data = []
        for lead in leads:
            leads_data.append({
                'id': lead.id,
                'name': f"{lead.first_name or ''} {lead.last_name or ''}".strip(),
                'email': lead.email or '',
                'phone': lead.phone or '',
                'source': lead.source or '',
                'interest': lead.interest or '',
                'reason': lead.notes or '',  # Using notes field to store reason
                'created_at': lead.created_at.strftime('%Y-%m-%d %H:%M') if lead.created_at else '',
                'updated_at': lead.updated_at.strftime('%Y-%m-%d %H:%M') if lead.updated_at else '',
                'status': lead.status
            })
        
        return JsonResponse({
            'success': True,
            'leads': leads_data,
            'count': len(leads_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    
# views.py
from django.shortcuts import render, redirect
from .forms import SheetConfigForm

def connect_sheet(request):
    if request.method == 'POST':
        form = SheetConfigForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sync-status')  # We'll create this later
    else:
        form = SheetConfigForm()
    
    return render(request, 'connect_sheet.html', {'form': form})

# myapp/views.py
from django.shortcuts import render, redirect
from .forms import SheetConfigForm
from .models import SheetConfig
from django.contrib import messages

def add_sheet(request):
    service_account_email = "your-service-account@your-project.iam.gserviceaccount.com"  # Replace with actual email
    
    if request.method == 'POST':
        form = SheetConfigForm(request.POST)
        if form.is_valid():
            # Create sheet config
            sheet_config = SheetConfig(
                sheet_url=form.cleaned_data['sheet_url'],
                sheet_type=form.cleaned_data['sheet_type'],
                is_active=True
            )
            sheet_config.save()
            messages.success(request, 'Sheet configuration added successfully!')
            return redirect('sheet_list')
    else:
        form = SheetConfigForm()
    
    return render(request, 'sheets/add_sheet.html', {
        'form': form,
        'service_account_email': service_account_email
    })

# myapp/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import SheetConfig
from .forms import SheetConfigForm
from .utils.sync import sync_sheet
import json  # We'll create this next

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import SheetConfig

@csrf_exempt
def sheetconfig(request):
    if request.method == "POST":
        company = request.POST.get("company")
        sheet_url = request.POST.get("sheet_url")
        sheet_type = request.POST.get("sheet_type")
        
        if not all([company, sheet_url, sheet_type]):
            return JsonResponse({
                "status": "error",
                "message": "Company, URL and sheet type are all required"
            }, status=400)
        
        try:
            sheet_config = SheetConfig(
                company=company,
                sheet_url=sheet_url,
                sheet_type=sheet_type
            )
            sheet_config.save()
            
            return JsonResponse({
                "status": "success",
                "message": "Configuration saved successfully",
                "id": sheet_config.id
            })
            
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Failed to save: {str(e)}"
            }, status=500)
    
    return JsonResponse({
        "status": "error",
        "message": "Only POST requests are allowed"
    }, status=405)
        

def sheet_list(request):
    sheets = SheetConfig.objects.all().order_by('-is_active')
    return render(request, 'sheets/sheet_list.html', {'sheets': sheets})

def toggle_sheet(request, sheet_id):
    sheet = SheetConfig.objects.get(id=sheet_id)
    sheet.is_active = not sheet.is_active
    sheet.save()
    messages.success(request, f"Sheet {'activated' if sheet.is_active else 'deactivated'}")
    return redirect('sheet_list')

def sync_sheet_now(request, sheet_id):
    sheet = SheetConfig.objects.get(id=sheet_id)
    success = sync_sheet(sheet)
    if success:
        messages.success(request, "Sheet synced successfully!")
    else:
        messages.error(request, "Failed to sync sheet")
    return redirect('sheet_list')



from rest_framework.generics import ListAPIView
from db.models import Lead
from db.serializers import LeadSerializer

class EmployeeLeadsView(ListAPIView):
    serializer_class = LeadSerializer

    def get_queryset(self):
        employee_name = self.request.GET.get('assigned_to')
        if not employee_name:
            return Lead.objects.none()

        # Convert "Haneef_M" to ["Haneef", "M"]
        parts = employee_name.split('_')

        if len(parts) == 2:
            first_name, last_name = parts
            return Lead.objects.filter(
                assigned_to__first_name=first_name,
                assigned_to__last_name=last_name
            ).order_by('-created_at')
        else:
            return Lead.objects.none()

from rest_framework import generics
from .models import CallLog, Lead
from .serializers import CallLogSerializer, LeadSerializer
from rest_framework.response import Response
from rest_framework import status

class CallLogCreateView(generics.CreateAPIView):
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user.employee)

class LeadRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer