from django.urls import path
from . import views

urlpatterns = [
    path('',        views.schedule_home,   name='schedule_home'),
    path('create/', views.schedule_create, name='schedule_create'),
    path('edit/<int:pk>/',   views.schedule_edit,   name='schedule_edit'),
    path('delete/<int:pk>/', views.schedule_delete, name='schedule_delete'),
]