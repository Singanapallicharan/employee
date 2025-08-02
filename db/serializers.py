from rest_framework import serializers
from .models import Lead, Employee, CallLog

class EmployeeSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['id', 'employee_id', 'first_name', 'last_name', 'phone', 'display_name']
    
    def get_display_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class LeadSerializer(serializers.ModelSerializer):
    assigned_to_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = "__all__"
    
    def get_assigned_to_name(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.first_name} {obj.assigned_to.last_name}"
        return None


class CallLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CallLog
        fields = '__all__'
        read_only_fields = ('timestamp',)