from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
import os
from .models import ProfileModel
from cadmin.models import blog_request
from django.contrib.auth import logout,authenticate,login

from django.http import HttpResponse
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

def sign_up(request, uid):
    try:
        # Decode the UID to get the blog request ID
        user_id = force_str(urlsafe_base64_decode(uid))
        blog = get_object_or_404(blog_request, id=user_id)

        if blog.status:  # Ensure the request is still valid
            if request.method == 'POST':
                email = request.POST.get('email')
                if email != blog.mail:
                    messages = 'The email provided does not match our records.'
                    return render(request, 'users/sign_up.html', {'messages': messages})

                username = request.POST.get('username')
                if User.objects.filter(username=username).exists():
                    messages = 'Username already exists.'
                    return render(request, 'users/sign_up.html', {'messages': messages})

                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                if password1 == password2:
                    # Create the user
                    user = User(username=username, email=email)
                    user.set_password(password1)
                    user.save()

                    # Update the blog request status
                    blog.status = False
                    blog.save()

                    return redirect('user_user_login')
                else:
                    messages = 'Passwords do not match.'
                    return render(request, 'users/sign_up.html', {'messages': messages})

            return render(request, 'users/sign_up.html', {'email': blog.mail})

        else:
            return HttpResponse('This request has already been completed.')
    except Exception as e:
        return HttpResponse('Invalid registration link.')



def user_user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            if user.is_superuser == False and user.is_staff == False:
                login(request, user)
                return redirect('blog-home')
            elif user.is_superuser == True and user.is_staff == True:
                login(request, user)
                return redirect('blog-home')
            else:
                msg = "You are not autherized for the access!"
                return render(request, 'users/login.html', {'msg': msg})
        else:
            msg = "Wrong credentials"
            return render(request, 'users/login.html', {"msg": msg})
    return render(request, 'users/login.html')


@login_required
def profile(request):
    profile, created = ProfileModel.objects.get_or_create(user=request.user)
    
    if request.method == "POST":
        profile.linkedin_id = request.POST.get('linkedin_id', '')
        profile.organization = request.POST.get('organization', '')
        profile.designation = request.POST.get('designation', '')

        if 'image' in request.FILES:
            profile.image = request.FILES['image']

        profile.save()
        return redirect('users-profile')  

    context = {'profile': profile}
    return render(request, 'users/profile.html', context)

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



