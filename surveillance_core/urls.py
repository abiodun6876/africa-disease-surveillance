from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from data_collection.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),  # Root URL
    path('data/', include('data_collection.urls')),
]

# Serve static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Fallback for all other URLs - redirect to home
handler404 = 'data_collection.views.home'