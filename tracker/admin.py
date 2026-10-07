from django.contrib import admin
from .models import WorkSession, Check
class CheckInline(admin.TabularInline):
    model = Check
    extra = 0
@admin.register(WorkSession)
class WorkSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'start_time', 'end_time', 'is_active']
    list_filter = ['is_active', 'user']
    inlines = [CheckInline]
@admin.register(Check)
class CheckAdmin(admin.ModelAdmin):
    list_display = ['session', 'code', 'created_at', 'answered_at', 'passed']
    list_filter = ['passed']
