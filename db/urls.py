from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('api/search/', views.search, name='search'),
    path('api/employee/applied/', views.get_applied_employees),
    path('api/employee/selected/', views.get_selected_employees, name='selected_employees'),
    path('api/active-employees/', views.get_active_employees, name='get_active_employees'),
    path('api/inactive-employees/', views.get_inactive_employees, name='get_inactive_employees'),
    path('api/student/add/', views.add_student, name='add_student'),
    path('api/student/update/<int:student_id>/', views.update_student_status, name='update_student_status'),
    path('api/student/delete/<int:student_id>/', views.delete_student, name='delete_student'),
    path('api/students/registered/', views.get_registered_students, name='registered_students'),
    path('api/students/not_registered/', views.get_not_registered_students, name='registered_students'),
    path('api/students/completed/', views.get_completed_students, name='completed_students'),
    path('api/leads/new/', views.get_new_leads, name='new_leads'),
    path('api/lead/add/', views.add_lead, name='add_lead'),
    path('api/lead/update/<int:lead_id>/', views.update_lead_status, name='update_lead_status'),
    path('api/lead/delete/<int:lead_id>/', views.delete_lead, name='delete_lead'),
    path('api/leads/interested/', views.get_interested_leads, name='interested_leads'),
    path('api/leads/not_interested/', views.get_not_interested_leads, name='not_interested_leads'),
    path('api/employee/add/', views.add_employee),
    path('api/employee/update/<int:emp_id>/', views.update_status),
    path('api/employee/delete/<int:emp_id>/', views.delete_employee),
    path('connect-sheet/', views.connect_sheet, name='connect-sheet'),
    path('sheets/add/', views.add_sheet, name='add_sheet'),
    path('sheets/', views.sheet_list, name='sheet_list'),
    path('api/sheetconfig/', views.sheetconfig, name="sheetconfig"),
    path('api/leads/', views.EmployeeLeadsView.as_view(), name='employee-leads'),
    path('api/call-logs/', views.CallLogCreateView.as_view(), name='call-log-create'),
    path('api/leads/<int:pk>/', views.LeadRetrieveUpdateView.as_view(), name='lead-detail'),

]
