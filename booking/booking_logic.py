# booking/booking_logic.py
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Availability, Booking

def get_available_slots(service, staff, booking_date):
    """Calculates all available time slots for a staff member on a specific date."""
    available_slots = []
    service_duration = timedelta(minutes=service.duration_minutes)
    weekday = booking_date.weekday()

    # 1. Get the staff's general working hours for that day of the week.
    try:
        availability = Availability.objects.get(staff=staff, day_of_week=weekday)
    except Availability.DoesNotExist:
        return [] # Staff does not work on this day.

    # 2. Get all the confirmed appointments that are already booked for that day.
    bookings_on_day = Booking.objects.filter(
        staff=staff,
        start_time__date=booking_date,
        status='confirmed'
    ).order_by('start_time')

    # 3. Iterate through the staff's workday, finding the gaps between existing bookings.
    current_time_naive = datetime.combine(booking_date, availability.start_time)
    current_time = timezone.make_aware(current_time_naive)
    end_of_day_naive = datetime.combine(booking_date, availability.end_time)
    end_of_day = timezone.make_aware(end_of_day_naive)

    for booking in bookings_on_day:
        # Check for slots before this booking starts.
        while current_time + service_duration <= booking.start_time:
            available_slots.append(current_time.time())
            current_time += timedelta(minutes=15) # We check for start times every 15 mins.
        # Jump our clock to the end of the current booking.
        current_time = booking.end_time

    # 4. After the last booking, check for remaining slots until the end of the day.
    while current_time + service_duration <= end_of_day:
        available_slots.append(current_time.time())
        current_time += timedelta(minutes=15)
        
    return available_slots