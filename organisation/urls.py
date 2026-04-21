from django.urls import path
from . import views

app_name = 'organisation'

urlpatterns = [

    # ── Organisation Overview ──────────────────
    path('', views.organisation_overview, name='organisation_overview'),

    # ── Departments ───────────────────────────
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/', views.department_detail, name='department_detail'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),

    # ── Teams ─────────────────────────────────
    path('teams/', views.team_list, name='team_list'),
    path('teams/<int:pk>/', views.team_detail, name='team_detail'),

    # ── Dependencies ──────────────────────────
    path('dependencies/', views.dependency_map, name='dependency_map'),
    path('dependencies/create/', views.dependency_create, name='dependency_create'),

    # ── Audit Log ─────────────────────────────
    path('audit/', views.audit_log, name='audit_log'),
]
