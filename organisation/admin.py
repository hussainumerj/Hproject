from django.contrib import admin

# Register your models here.

from .models import Department, Team, TeamType, Dependency, AuditLog


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'leader', 'specialisation', 'team_count', 'created_at')
    search_fields = ('name', 'specialisation', 'leader__username')
    list_filter = ('specialisation',)
    ordering = ('name',)

    def team_count(self, obj):
        return obj.teams.count()
    team_count.short_description = 'Teams'


@admin.register(TeamType)
class TeamTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'team_type', 'manager', 'status', 'member_count', 'updated_at')
    search_fields = ('name', 'department__name', 'manager__username')
    list_filter = ('status', 'department', 'team_type')
    filter_horizontal = ('members',)
    ordering = ('name',)

    def member_count(self, obj):
        return obj.members.count()
    member_count.short_description = 'Members'


@admin.register(Dependency)
class DependencyAdmin(admin.ModelAdmin):
    list_display = ('upstream_team', 'downstream_team', 'description', 'created_at')
    search_fields = ('upstream_team__name', 'downstream_team__name')
    list_filter = ('upstream_team__department',)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    search_fields = ('user__username', 'model_name', 'description')
    list_filter = ('action', 'model_name')
    ordering = ('-timestamp',)
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'description', 'timestamp')

    # Prevent anyone editing audit logs
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

