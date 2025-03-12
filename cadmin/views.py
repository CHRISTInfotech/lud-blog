from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count
import json
import csv
from io import TextIOWrapper

from django.contrib.auth.models import User
from users.models import Category, Blog, UserProfile
from .models import blog_request, Invitation
from django.db import models

# Create your views here.




@login_required
def edit_profile_admin(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        name = request.POST.get('name', '')
        affiliation = request.POST.get('affiliation', '')
        profile_picture = request.FILES.get('profile_picture')
        
        user_profile.name = name
        user_profile.affiliation = affiliation
        
        if profile_picture:
            user_profile.profile_picture = profile_picture
        request.user.first_name = name
     
        request.user.save()
        user_profile.save()
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('edit_profile_admin')  # Redirect to the same page after saving
    
    
    return render(request,'admin/edit_profile_admin.html',{'user_profile': user_profile})

# def invite_user(request):
#     return render(request,'admin/invite_user.html')


@login_required
@csrf_exempt  # Remove this if you are using CSRF tokens in frontend
def toggle_user_status(request, user_id):
    if request.method == "POST":
        try:
            user = User.objects.get(id=user_id)
            user.is_active = not user.is_active  # Toggle active status
            user.save()

            return JsonResponse({"success": True, "is_active": user.is_active})
        except User.DoesNotExist:
            return JsonResponse({"success": False, "error": "User not found"}, status=404)

    return JsonResponse({"success": False, "error": "Invalid request"}, status=400)





@login_required
def manage_user(request):
    users = UserProfile.objects.filter(user__is_superuser=False).all()
    return render(request, 'admin/manage_user.html', {'users': users})
    
    

@login_required
def blog_detail_published(request):
    # Get the blog ID from the request

    status_counts = Blog.objects.aggregate(
        total=Count('id'),
        pending=Count('id', filter=models.Q(status='Pending')),
        approved=Count('id', filter=models.Q(status='accepted')),
        rejected=Count('id', filter=models.Q(status='rejected'))
    )
    
    context = {
        'blog': Blog.objects.all(),
        'total_count': status_counts['total'],
        'pending_count': status_counts['pending'],
        'approved_count': status_counts['approved'],
        'rejected_count': status_counts['rejected'],
    }
    return render(request, 'admin/blog_detail_published.html', context)




from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.decorators import login_required
from .models import Invitation
import csv
from io import TextIOWrapper

@login_required
def invite_user(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "You are invited to join our blog platform.")
        csv_file = request.FILES.get("csv_file")

        email_list = []
        invited_users = []

        is_bulk_invite = bool(csv_file)

        if is_bulk_invite:
            try:
                decoded_file = TextIOWrapper(csv_file.file, encoding="utf-8")
                reader = csv.reader(decoded_file)
                
                for row in reader:
                    if len(row) >= 2:
                        email_list.append({"name": row[0].strip(), "email": row[1].strip()})

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")
                return redirect("invite_user")

        if email:
            email_list.append({"name": name, "email": email})

        new_invites = []
        already_invited = set()

        for user in email_list:
            if Invitation.objects.filter(email=user["email"]).exists():
                already_invited.add(user["email"])
            else:
                invite_link = f"https://yourdomain.com/register?email={user['email']}"  # Modify based on your actual registration link
                new_invites.append(user)
                invited_users.append(Invitation(name=user["name"], email=user["email"], message=message))

                # **Send HTML Email**
                context = {
                    "name": user["name"],
                    "message": message,
                    "invite_link": invite_link,
                }

                subject = "You're Invited to Join Our Blog!"
                html_message = render_to_string("emails/invite_email.html", context)
                plain_message = strip_tags(html_message)  # Convert HTML to plain text
                from_email = "noreply@yourdomain.com"
                recipient_list = [user["email"]]

                email_obj = EmailMultiAlternatives(subject, plain_message, from_email, recipient_list)
                email_obj.attach_alternative(html_message, "text/html")
                email_obj.send()

        if invited_users:
            Invitation.objects.bulk_create(invited_users)

        if is_bulk_invite:
            messages.success(request, "Bulk invitations sent successfully.")
        else:
            if email in already_invited:
                messages.warning(request, f"{email} is already invited.")
            elif new_invites:
                messages.success(request, "Invitation sent successfully.")

        return redirect("view_invited_user")

    return render(request, "admin/invite_user.html")








@login_required
def view_invited_user(request):
    invitations = Invitation.objects.all()
    
    # Update acceptance status dynamically
    for invite in invitations:
        invite.accepted = invite.check_status()
        invite.save()

    return render(request, 'admin/view_invited_user.html', {'invitations': invitations})

from django.http import HttpResponse
@login_required
def download_csv_template(request):
    # Define CSV content
    csv_content = "nJohn Doe,johndoe@example.com\nJane Smith,janesmith@example.com\n"

    # Create HTTP response with CSV content
    response = HttpResponse(csv_content, content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="invite_template.csv"'
    
    return response

@login_required
def admin_edit_blog(request, blog_id):
    if not request.user.is_staff:
        return redirect('blog_requests')  # Only admins can access

    blog = get_object_or_404(Blog, id=blog_id)
    categories = Category.objects.all()
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        category_name = request.POST.get('category')
        blog.category = get_object_or_404(Category, name=category_name)
        if 'image' in request.FILES:  # Allow admin to update the image
            blog.image = request.FILES['image']

        # Check if admin wants to approve while updating
        if 'approve' in request.POST:
            blog.status = 'accepted'
        elif 'reject' in request.POST:
            blog.status = 'rejected'
        elif 'pending' in request.POST:
            blog.status = 'Pending'

        blog.save()
        return redirect('blog_detail_published')

    return render(request, 'admin/admin_edit_blog.html',  {'blog': blog, 'categories': categories})



@login_required
def manage_categories(request):
    categories = Category.objects.all()

    if request.method == "POST":
        category_name = request.POST.get("category_name").strip()  # Remove leading/trailing spaces
        category_name_lower = category_name.lower()

        # Check if category exists (case insensitive)
        existing_categories = Category.objects.values_list('name', flat=True)
        existing_categories_lower = [cat.lower() for cat in existing_categories]

        if category_name_lower in existing_categories_lower:
            messages.error(request, "Category already exists!")
        else:
            Category.objects.create(name=category_name)
            messages.success(request, "Category added successfully!")

        return redirect('admin_manage_categories')

    return render(request, 'admin/category_management.html', {'categories': categories})




@login_required
def disable_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    # Disable the category
    category.is_active = False
    category.save()

    messages.success(request, f"Category '{category.name}' has been disabled successfully!")
    return redirect('admin_manage_categories')

@login_required
def enable_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    # Enable the category
    category.is_active = True
    category.save()

    messages.success(request, f"Category '{category.name}' has been enabled successfully!")
    return redirect('admin_manage_categories')

@login_required
def admin_chart(request):
    # Count blogs based on their status
    blog_status_data = Blog.objects.values("status").annotate(count=Count("id"))
    
    # Count blogs in each category
    category_data = Blog.objects.values("category__name").annotate(count=Count("id"))

    # Top authors by blog count
    top_authors = Blog.objects.values("author__username").annotate(count=Count("id")).order_by("-count")[:5]

    # Count total users
    total_users = User.objects.count()

    # Count total blogs
    total_blogs = Blog.objects.count()

    # Total likes vs dislikes
    total_likes = Blog.objects.aggregate(total_likes=Count("likes"))["total_likes"]
    total_dislikes = Blog.objects.aggregate(total_dislikes=Count("dislikes"))["total_dislikes"]

    context = {
        "blog_status_data": list(blog_status_data),
        "category_data": list(category_data),
        "top_authors": list(top_authors),
        "total_users": total_users,
        "total_blogs": total_blogs,
        "total_likes": total_likes,
        "total_dislikes": total_dislikes,
    }
    return render(request,'admin/admin_chart.html',context)