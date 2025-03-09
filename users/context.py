from .models import UserProfile,Category

def user_profile_context(request):
    context = {}
    
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        context['user_profile'] = user_profile
    
    context['categories'] = Category.objects.all()  # Fetch all categories
    
    return context