from django.contrib import admin
from django.urls import path, include
from data_collection.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('data/', include('data_collection.urls')),
    path('ml/', include('ml_predictions.urls')),  # Make sure this line exists
    path('', home, name='home'),
]