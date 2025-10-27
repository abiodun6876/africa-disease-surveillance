from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('submit/', views.submit_data, name='submit_data'),
    path('bulk-upload/', views.bulk_upload, name='bulk_upload'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('cases/', views.case_reports, name='case_reports'),
    path('alerts/', views.alerts_view, name='alerts'),
    path('api/stats/', views.api_stats, name='api_stats'),
    path('initialize/', views.initialize_parse_data, name='initialize_parse_data'),
]