from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_report, name='generate_report'),
    path('reports/', views.report_list, name='report_list'),
    path('download/<str:report_id>/', views.download_report, name='download_report'),
]