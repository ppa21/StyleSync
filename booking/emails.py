# booking/emails.py
from django.core.mail import send_mail
from django.template.loader import render_to_string # Allows building emails from templates
from django.conf import settings

def send_booking_email(booking, template_prefix):
    """A helper function to send booking confirmation emails."""
    context = {'booking': booking}
    subject = render_to_string(f'booking/email/{template_prefix}_subject.txt', context).strip()
    text_body = render_to_string(f'booking/email/{template_prefix}_body.txt', context)
    
    send_mail(
        subject=subject,
        message=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[booking.customer.email],
        fail_silently=False # Raise an error if the email fails to send
    )