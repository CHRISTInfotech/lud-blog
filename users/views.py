from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db import models

from cadmin.models import blog_request, Invitation
from users.decorators import active_user_required
from .models import Blog, Category, UserProfile

import os
import random



User = get_user_model()

# Store OTPs temporarily
otp_storage = {}

def request_otp(request):
    if request.method == "POST":
        email = request.POST.get("email")
        is_admin_email = User.objects.filter(email=email, is_superuser=True).exists()
        # Check if the user is invited
        if not (is_admin_email or Invitation.objects.filter(email=email).exists()):
            return render(request, "users/request_otp.html", {"error": "You are not an invited user!"})

        otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP

        # Store OTP with timestamp
        otp_storage[email] = {"otp": otp, "timestamp": now()}

        # Send OTP via email
        send_mail(
            "Your OTP Code",
            f"Your OTP is: {otp}",
            "noreply@yourdomain.com",
            [email],
            fail_silently=False,
        )

        request.session["email"] = email  # Store email in session for verification
        return redirect("verify_otp")  # Redirect to OTP verification page

    return render(request, "users/request_otp.html")


def verify_otp(request):
    email = request.session.get("email")  # Retrieve email from session
    if not email:
        return redirect("request_otp")  # Redirect if no email is found

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        stored_otp = otp_storage.get(email)

        if stored_otp and stored_otp["otp"] == entered_otp:
            # Check if user exists
            user, created = User.objects.get_or_create(email=email,defaults={'username': email})
            
            # If the user is new, set a default password (change later)
            if created:
                user.set_password(User.objects.make_random_password())
                user.save()
            if not user.is_active:
                messages.error(request, "Your account is disabled. Please contact support.")
                return redirect("verify_otp")  # Redirect back to OTP page

            # Log the user in
            login(request, user)

            # Clear OTP storage
            del otp_storage[email]
            
            if user.is_superuser and user.is_staff:
                return redirect("blog_detail_published")  # Redirect admin user
            else:
                return redirect("user_blog_update")  # Redirect regular user

        return render(request, "users/verify_otp.html", {"error": "Invalid OTP"})

    return render(request, "users/verify_otp.html")



def logout_view(request):
    logout(request)
    return redirect('blog-home')


def send_request(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        entity = blog_request(name=name,mail=email)
        entity.save()

        return redirect('blog-home')
    return render(request,'users/request.html')

@active_user_required
@login_required
def edit_profile(request):
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
        user_profile.save()
        request.user.save()
        messages.success(request, 'Your profile has been updated successfully!')
        return redirect('edit_profile')  # Redirect to the same page after saving
    
    return render(request, 'users/edit_profile.html', {'user_profile': user_profile})
    


@active_user_required
@login_required
def create_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        category_id = request.POST.get('category')  # Get selected category ID
        content = request.POST.get('content')
        image = request.FILES.get('image')
        author = request.user

        category = Category.objects.get(id=category_id)  # Fetch category object

        Blog.objects.create(
            title=title,
            category=category,
            content=content,
            image=image,
            author=author,
            status="Pending",
        )
        return redirect('create_post')

    categories = Category.objects.all()  # Get all categories from DB
    template = "admin/admin_create_post.html" if request.user.is_superuser else "users/create_post.html"
    return render(request,template, {'categories': categories})



@active_user_required

def blog_detail(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    related_blogs = Blog.objects.filter(
        category=blog.category,status="accepted",
        category__is_active=True,
    ).exclude(pk=pk).order_by('-created_at')[:4]
    
    context = {
        'blog': blog,
        'related_blogs': related_blogs
    }
    return render(request, 'users/blog_read.html', context)
   

@active_user_required
@login_required
def blog_detail_while_editing(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.user.is_superuser:
        # Admin sees related blogs by the same author as the blog being checked
        related_blogs = Blog.objects.filter(author=blog.author).exclude(pk=pk).order_by('-created_at')[:4]
    else:
        # Regular users see their own related blogs
        related_blogs = Blog.objects.filter(author=request.user).exclude(pk=pk).order_by('-created_at')[:4]
    
    context = {
        'blog': blog,
        'related_blogs': related_blogs
    }
    return render(request, 'users/blog_read_edit.html', context)



@active_user_required

def user_blog_update(request):
    """Display all blogs written by the logged-in user."""
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated
    if request.user.is_staff:  # Check if the user is an admin (staff)
        template_name = "partials/admin_base.html"
    else:
        template_name = "partials/base.html"
    blogs = Blog.objects.filter(author=request.user)  # Fetch blogs for the user
    return render(request, 'users/user_blog_update.html', {'blogs': blogs,"base_template": template_name})


@active_user_required
@login_required
def user_edit_blog(request, blog_id):
      # Only admins can access
    if request.user.is_staff:  # Check if the user is an admin (staff)
         template_name = "partials/admin_base.html"
    else:
         template_name = "partials/base.html"
    blog = get_object_or_404(Blog, id=blog_id)
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.content = request.POST.get('content')
        category_name = request.POST.get('category')
        blog.category = get_object_or_404(Category, name=category_name)
        if 'image' in request.FILES:  # Allow admin to update the image
            blog.image = request.FILES['image']

        # Check if admin wants to approve while updating
        if 'update' in request.POST:
            blog.status = 'Pending'
        
        
        blog.save()
        return redirect('user_blog_update')

    return render(request, 'users/user_edit_blog.html', {'blog': blog,"base_template": template_name})



def like_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        # Get existing votes from session
        votes = request.session.get('blog_votes', {})
        current_vote = votes.get(str(pk), None)

        if current_vote == 'like':
            # Remove existing like
            blog.likes -= 1
            del votes[str(pk)]
        else:
            # Add new like and remove existing dislike if present
            if current_vote == 'dislike':
                blog.dislikes -= 1
            blog.likes += 1
            votes[str(pk)] = 'like'

        # Save changes
        blog.save()
        request.session['blog_votes'] = votes
        return JsonResponse({
            'success': True,
            'likes': blog.likes,
            'dislikes': blog.dislikes,
            'current_vote': votes.get(str(pk))
        })
    return JsonResponse({'success': False}, status=400)



def dislike_blog(request, pk):
    blog = get_object_or_404(Blog, pk=pk)
    if request.method == 'POST':
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        votes = request.session.get('blog_votes', {})
        current_vote = votes.get(str(pk))

        if current_vote == 'dislike':
            # Remove existing dislike
            blog.dislikes -= 1
            del votes[str(pk)]
        else:
            # Add new dislike and remove existing like if present
            if current_vote == 'like':
                blog.likes -= 1
            blog.dislikes += 1
            votes[str(pk)] = 'dislike'

        blog.save()
        request.session['blog_votes'] = votes
        return JsonResponse({
            'success': True,
            'dislikes': blog.dislikes,
            'likes': blog.likes,
            'current_vote': votes.get(str(pk))
        })
    return JsonResponse({'success': False}, status=400)


def user_profile(request,pk):
    user = get_object_or_404(User, id=pk)
    user_blogs = Blog.objects.filter(author=user).order_by('-created_at')
    
    context = {
        'profile_user': user,
        'user_blogs': user_blogs
    }
    return render(request, 'users/user_profile.html', context)