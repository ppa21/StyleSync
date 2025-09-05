# booking/models.py
from django.db import models
from django.contrib.auth.models import User # Django's built-in user system
from datetime import timedelta

# We extend Django's User to add a 'role' to each person.
class UserProfile(models.Model):
    USER_TYPE_CHOICES = (('customer', 'Customer'), ('staff', 'Staff'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='customer')
    def __str__(self): return self.user.username

# This model defines what a staff member is.
class Staff(models.Model):
    # It must be linked to a user who is designated as 'staff'.
    user_profile = models.OneToOneField(UserProfile, on_delete=models.CASCADE, limit_choices_to={'user_type': 'staff'})
    bio = models.TextField(blank=True, null=True)
    def __str__(self): return self.user_profile.user.get_full_name() or self.user_profile.user.username

# This model defines a service offered by the salon.
class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    # A service can be done by many staff members, and staff can do many services.
    staff_members = models.ManyToManyField(Staff, related_name='services')
    is_active = models.BooleanField(default=True)
    def __str__(self): return self.name

# This model defines the weekly, recurring work schedule for a staff member.
class Availability(models.Model):
    DAY_OF_WEEK_CHOICES = [(0, 'Monday'),(1, 'Tuesday'),(2, 'Wednesday'),(3, 'Thursday'),(4, 'Friday'),(5, 'Saturday'),(6, 'Sunday')]
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='availabilities')
    day_of_week = models.IntegerField(choices=DAY_OF_WEEK_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    class Meta:
        verbose_name_plural = "Availabilities"
        unique_together = ('staff', 'day_of_week')
    def __str__(self): return f"{self.staff}'s availability on {self.get_day_of_week_display()}"

# This model represents a single appointment.
class Booking(models.Model):
    STATUS_CHOICES = [('pending', 'Pending Payment'),('confirmed', 'Confirmed'),('completed', 'Completed'),('cancelled', 'Cancelled')]
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)
    
    # We override the save method to automatically calculate the end time.
    def save(self, *args, **kwargs):
        if not self.end_time: self.end_time = self.start_time + timedelta(minutes=self.service.duration_minutes)
        super().save(*args, **kwargs)
    def __str__(self): return f"Booking for {self.service.name} with {self.staff} on {self.start_time.strftime('%Y-%m-%d %H:%M')}"