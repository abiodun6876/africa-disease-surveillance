from django.urls import path
from . import views

urlpatterns = [
    path('predict/', views.predict_outbreak, name='predict_outbreak'),
    path('models/', views.model_list, name='model_list'),
    path('train/', views.train_model, name='train_model'),
]