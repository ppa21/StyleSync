# booking/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import Availability

# A custom registration form that adds fields for first name, last name, and email.
class CustomerRegistrationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254, required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email')

# A form for a single availability entry.
class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ['day_of_week', 'start_time', 'end_time']
        # Use a nice time-picker widget in the browser.
        widgets = {
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'})
        }

# A "FormSet" is a powerful tool for managing multiple copies of the same form on one page.
# We use it for the staff member's 7-day weekly schedule.
AvailabilityFormSet = modelformset_factory(
    Availability,
    form=AvailabilityForm,
    extra=7, max_num=7, # Show up to 7 forms
    can_delete=True # Allow staff to delete existing schedule entries
)