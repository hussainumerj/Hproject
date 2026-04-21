from django.contrib import admin
from .models import Meeting

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'date_time', 'created_by']
    list_filter  = ['platform', 'date_time']
    search_fields = ['title']