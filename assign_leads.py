import logging
from django.db.models import Count, Q
import django
import os
import sys
from datetime import datetime, timedelta
import traceback  # For proper exception printing

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eligodb.settings")
django.setup()

from db.models import Lead, Employee

def assign_leads_round_robin():
    """
    Enhanced Phase 1: Fair distribution with improved accuracy
    """
    
    # Constants
    MAX_LEADS_PER_EMPLOYEE = 5
    REASSIGNMENT_TIMEOUT_HOURS = 48
    
    try:
        print("=== Starting Lead Assignment ===")
        
        # 1. Get eligible leads
        eligible_leads = Lead.objects.filter(
            Q(status='new') & 
            (Q(assigned_leads='not assigned') |
             Q(assignment_date__lt=datetime.now()-timedelta(hours=REASSIGNMENT_TIMEOUT_HOURS)))
        ).order_by('created_at')
        
        print(f"Found {eligible_leads.count()} eligible leads")
        
        # 2. Get active employees
        employees = Employee.objects.filter(
            status='Active',  # Match your model's choice exactly
            assigned_leads='Not assigned'
        ).annotate(
            current_load=Count('leads', 
                filter=Q(leads__assigned_leads='assigned') &
                Q(leads__assignment_date__gte=datetime.now()-timedelta(days=7))
        )).order_by('current_load')
        
        if not employees.exists():
            print("No active employees available for assignment!")
            return
        
        print(f"Processing with {employees.count()} available employees")
        
        # 3. Assignment logic
        assignment_count = 0
        for i, lead in enumerate(eligible_leads):
            employee = employees[i % employees.count()]
            
            if employee.current_load >= MAX_LEADS_PER_EMPLOYEE:
                print(f"Skipping employee {employee.id} at capacity")
                continue
                
            # Update lead
            lead.assigned_to = employee
            lead.assigned_leads = 'assigned'
            lead.assignment_date = datetime.now()
            lead.save()
            
            # Update employee
            employee.refresh_from_db()
            employee.current_load = employee.leads.filter(
                assigned_leads='assigned',
                assignment_date__gte=datetime.now()-timedelta(days=7)
            ).count()
            employee.save()
            
            assignment_count += 1
            print(f"Assigned Lead {lead.id} (created {lead.created_at.date()}) to {employee.first_name} (current load: {employee.current_load})")
            
            if assignment_count >= 20:
                break
                
        print(f"Completed: Assigned {assignment_count} leads")
        
    except Exception as e:
        print(f"Assignment failed: {e}")
        traceback.print_exc()  # Proper exception printing

if __name__ == "__main__":
    assign_leads_round_robin()