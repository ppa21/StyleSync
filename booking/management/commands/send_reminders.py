# booking/management/commands/send_reminders.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from booking.models import Booking
from booking.emails import send_booking_email

# By creating a file in this specific folder and naming the class "Command",
# Django automatically makes it runnable from the command line.
class Command(BaseCommand):
    # This is a helpful description of what the command does.
    help = 'Sends email reminders for bookings that are 24-48 hours away.'

    def handle(self, *args, **options):
        """The main logic of the script goes in this 'handle' method."""
        
        now = timezone.now()
        # We define a time window: we're looking for appointments that are
        # more than 24 hours away but less than 48 hours away.
        reminder_start_time = now + timedelta(hours=24)
        reminder_end_time = now + timedelta(hours=48)

        # This is a database query. It asks the Booking model to find all confirmed
        # bookings that fall within our specific time window.
        bookings_to_remind = Booking.objects.filter(
            start_time__gte=reminder_start_time,
            start_time__lt=reminder_end_time,
            status='confirmed'
        )

        # This will print a status message to the console when the script runs.
        self.stdout.write(f'Found {bookings_to_remind.count()} bookings to remind...')

        # We loop through each booking that the database found.
        for booking in bookings_to_remind:
            try:
                # We reuse the same email function from before, but this time
                # we tell it to use the 'reminder' templates.
                send_booking_email(booking, 'reminder')
                self.stdout.write(self.style.SUCCESS(f'Successfully sent reminder for booking #{booking.id}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to send reminder for booking #{booking.id}: {e}'))

        self.stdout.write(self.style.SUCCESS('Reminder process complete.'))
