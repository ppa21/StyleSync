# booking/admin.py
from django.contrib import admin
from .models import UserProfile, Staff, Service, Availability, Booking

# Register each model to make it visible in the admin interface.
admin.site.register(UserProfile)
admin.site.register(Staff)
admin.site.register(Service)
admin.site.register(Availability)
admin.site.register(Booking)