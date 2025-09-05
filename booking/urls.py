# booking/urls.py
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# This namespace helps us organize URLs and refer to them easily in templates.
app_name = 'booking'

urlpatterns = [
    # URLs for main pages and user authentication
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='booking/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='booking:home'), name='logout'),

    # URLs for the booking and payment process
    path('book/service/<int:service_id>/', views.booking_view, name='book_service'),
    path('payment/success/', views.payment_success_view, name='payment_success'),
    path('payment/cancelled/', views.payment_cancelled_view, name='payment_cancelled'),
    path('stripe/webhook/', views.stripe_webhook_view, name='stripe_webhook'),
    
    # URLs for user and staff dashboards
    path('my-bookings/', views.my_bookings_view, name='my_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('staff/dashboard/', views.staff_dashboard_view, name='staff_dashboard'),
    path('staff/availability/', views.manage_availability_view, name='manage_availability'),
]