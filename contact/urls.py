from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Student Authentication Urls
    path('login/', views.student_login, name='student_login'),
    path('register/', views.student_register, name='student_register'),
    path('logout/', views.student_logout, name='student_logout'),
    path('portal/', views.student_portal, name='student_portal'),
    
    # AJAX Admin Actions
    path('admin/toggle-verify/<int:contact_id>/', views.admin_toggle_verify, name='admin_toggle_verify'),
    path('admin/update-status/<int:contact_id>/', views.admin_update_status, name='admin_update_status'),
    path('admin/assign-cohort/<int:contact_id>/', views.admin_assign_cohort, name='admin_assign_cohort'),
    path('dashboard/save-applicant/<int:contact_id>/', views.admin_save_applicant, name='admin_save_applicant'),
    path('admin/export-csv/', views.admin_export_csv, name='admin_export_csv'),
]