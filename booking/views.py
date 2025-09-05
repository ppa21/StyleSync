# booking/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from collections import defaultdict
import stripe

# We import all our custom components
from .models import Service, Staff, Booking, UserProfile, Availability
from .forms import CustomerRegistrationForm, AvailabilityFormSet
from .booking_logic import get_available_slots
from .emails import send_booking_email
from .decorators import staff_required

# Set up Stripe with our secret key from settings.py
stripe.api_key = settings.STRIPE_SECRET_KEY

# --- Page Views ---

def home(request):
    """View for the homepage, which lists all services."""
    services = Service.objects.filter(is_active=True).order_by('name')
    return render(request, 'booking/home.html', {'services': services})

def register_view(request):
    """Handles the user registration page."""
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, user_type='customer')
            login(request, user)
            messages.success(request, "Registration successful.")
            return redirect('booking:home')
        else:
            messages.error(request, "Registration unsuccessful. Please check the form for errors.")
    else:
        form = CustomerRegistrationForm()
    return render(request, 'booking/register.html', {'form': form})

@login_required # This decorator ensures only logged-in users can access this page.
def my_bookings_view(request):
    """Shows a logged-in customer their upcoming and past bookings."""
    now = timezone.now()
    upcoming = Booking.objects.filter(customer=request.user, start_time__gte=now, status='confirmed').order_by('start_time')
    past = Booking.objects.filter(customer=request.user, start_time__lt=now).order_by('-start_time')
    return render(request, 'booking/my_bookings.html', {'upcoming_bookings': upcoming, 'past_bookings': past})

# --- Staff-Only Views ---

@staff_required # Our custom decorator to protect this page.
def staff_dashboard_view(request):
    """The main dashboard for staff to see their schedule."""
    staff_member = get_object_or_404(Staff, user_profile__user=request.user)
    bookings = Booking.objects.filter(staff=staff_member, status='confirmed', start_time__gte=timezone.now().date()).order_by('start_time')
    bookings_by_date = defaultdict(list)
    for booking in bookings:
        bookings_by_date[booking.start_time.date()].append(booking)
    return render(request, 'booking/staff_dashboard.html', {'bookings_by_date': dict(bookings_by_date), 'staff_member': staff_member})

@staff_required
def manage_availability_view(request):
    """Allows staff to edit their weekly work schedule."""
    staff_member = get_object_or_404(Staff, user_profile__user=request.user)
    queryset = Availability.objects.filter(staff=staff_member).order_by('day_of_week')
    if request.method == 'POST':
        formset = AvailabilityFormSet(request.POST, queryset=queryset)
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.staff = staff_member
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            messages.success(request, "Availability updated.")
            return redirect('booking:staff_dashboard')
    else:
        formset = AvailabilityFormSet(queryset=queryset)
    return render(request, 'booking/manage_availability.html', {'formset': formset})

# --- Booking & Payment Process Views ---

@login_required
def booking_view(request, service_id):
    """The main view for the multi-step booking process."""
    service = get_object_or_404(Service, id=service_id)
    staff_members = service.staff_members.all()
    
    # Step 1: Check for available slots if staff/date are selected
    available_slots = []
    selected_date_str = request.GET.get('date')
    selected_staff_id = request.GET.get('staff')
    if selected_date_str and selected_staff_id:
        try:
            selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            selected_staff = get_object_or_404(Staff, id=selected_staff_id)
            available_slots = get_available_slots(service, selected_staff, selected_date)
        except (ValueError, Staff.DoesNotExist):
            messages.error(request, "Invalid date or staff selection.")
            
    # Step 2: Handle the final submission to create the booking and go to payment
    if request.method == 'POST':
        staff_id = request.POST.get('staff')
        date_str = request.POST.get('date')
        time_str = request.POST.get('time')
        try:
            staff = get_object_or_404(Staff, id=staff_id)
            # Combine date and time, and make it timezone-aware
            booking_datetime_naive = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M:%S')
            booking_datetime = timezone.make_aware(booking_datetime_naive)

            # Create a booking with 'pending' status
            booking = Booking.objects.create(customer=request.user, staff=staff, service=service, start_time=booking_datetime, status='pending')

            # Create a Stripe Checkout Session for payment
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': f"{service.name} with {staff}"},
                        'unit_amount': int(service.price * 100), # Price in cents
                    }, 'quantity': 1
                }],
                mode='payment',
                success_url=request.build_absolute_uri(reverse('booking:payment_success')),
                cancel_url=request.build_absolute_uri(reverse('booking:payment_cancelled')),
                metadata={'booking_id': booking.id} # Pass our booking ID to Stripe
            )
            booking.stripe_session_id = checkout_session.id
            booking.save()
            return redirect(checkout_session.url, code=303) # Redirect to Stripe's payment page
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('booking:book_service', service_id=service.id)

    context = {'service': service, 'staff_members': staff_members, 'selected_date': selected_date_str, 'selected_staff_id': int(selected_staff_id) if selected_staff_id else None, 'available_slots': available_slots}
    return render(request, 'booking/booking_form.html', context)

@login_required
def cancel_booking_view(request, booking_id):
    """Allows a user to cancel their own booking."""
    booking = get_object_or_404(Booking, id=booking_id, customer=request.user)
    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, "Your booking has been cancelled.")
    return redirect('booking:my_bookings')

# --- Stripe Integration Views ---

def payment_success_view(request):
    """Page the user sees after a successful payment."""
    messages.success(request, "Payment successful! Your booking is confirmed.")
    return redirect('booking:my_bookings')

def payment_cancelled_view(request):
    """Page the user sees if they cancel the payment process."""
    # It's good practice to find and delete the 'pending' booking here.
    messages.error(request, "Payment was cancelled. Please try again.")
    return redirect('booking:home')

@csrf_exempt # Stripe sends data here without a CSRF token, so we must exempt this view.
def stripe_webhook_view(request):
    """An endpoint for Stripe to send us notifications (e.g., 'payment successful')."""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400) # Bad request
    
    # Handle the 'checkout.session.completed' event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        booking_id = session.get('metadata', {}).get('booking_id')
        if booking_id:
            try:
                booking = Booking.objects.get(id=booking_id)
                # Check status to prevent processing twice
                if booking.status == 'pending':
                    booking.status = 'confirmed'
                    booking.save()
                    send_booking_email(booking, 'confirmation') # Send confirmation email
            except Booking.DoesNotExist:
                return HttpResponse(status=404) # Not found
    return HttpResponse(status=200) # Success