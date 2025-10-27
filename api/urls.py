from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'submissions', views.SubmissionViewSet)
router.register(r'predictions', views.PredictionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('data/export/', views.export_data, name='export_data'),
]