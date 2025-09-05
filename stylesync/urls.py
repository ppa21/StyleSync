# stylesync/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # The URL for Django's powerful, built-in admin panel.
    path('admin/', admin.site.urls),

    # For any other URL, hand off the request to the 'booking' app's own urls.py file.
    path('', include('booking.urls')),
]

# This helper line allows Django's development server to serve user-uploaded media files.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)