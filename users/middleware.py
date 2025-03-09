from django.shortcuts import redirect
from django.contrib import messages

class CheckUserActiveMiddleware:
    """Middleware to check if the logged-in user is still active."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            messages.error(request, "Your account has been disabled. Please contact support.")
            return redirect("logout")  # Redirect to logout or a custom disabled account page
        
        return self.get_response(request)
