# booking/decorators.py
from django.core.exceptions import PermissionDenied

def staff_required(function):
    """A decorator to ensure that only staff members can access a view."""
    def wrap(request, *args, **kwargs):
        # If user is logged in, has a profile, and is a staff member...
        if request.user.is_authenticated and hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'staff':
            # ...then allow them to proceed to the original view function.
            return function(request, *args, **kwargs)
        else:
            # ...otherwise, show a "Permission Denied" error.
            raise PermissionDenied
    return wrap