from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def active_user_required(view_func):
    """Decorator to check if the user is active before accessing the view."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and not request.user.is_active:
            messages.error(request, "Your account is disabled. Please contact support.")
            return redirect("logout")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
