from django.contrib import admin
from .models import Lead, Employee, Student, SheetConfig

admin.site.register(Lead)
admin.site.register(Employee)
admin.site.register(Student)
@admin.register(SheetConfig)
class SheetConfigAdmin(admin.ModelAdmin):
    list_display = ('company_sheet_type_display', 'sheet_url', 'is_active', 'created_at')
    list_filter = ('sheet_type', 'is_active', 'created_at')
    search_fields = ('company', 'sheet_url', 'sheet_type')
    list_editable = ('is_active',)
    readonly_fields = ('sheet_id', 'created_at')
    
    fieldsets = (
        ('Company Information', {
            'fields': ('company',)
        }),
        ('Sheet Configuration', {
            'fields': ('sheet_url', 'sheet_type', 'sheet_id')
        }),
        ('Status', {
            'fields': ('is_active', 'last_synced_row')
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )
    
    def company_sheet_type_display(self, obj):
        return f"{obj.company} - {obj.get_sheet_type_display()}"
    company_sheet_type_display.short_description = 'Company - Sheet Type'
    company_sheet_type_display.admin_order_field = 'company'
