from django.shortcuts import render,redirect,get_object_or_404
from .models import blog_request
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.paginator import Paginator
from blog.models import Category,Post
# Create your views here.

def blog_requests(request):
    full = Category.objects.all()
    blog = blog_request.objects.all().order_by('-status')
    paginator = Paginator(blog, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    if request.method == 'POST':
        category_name = request.POST.get('name')
        if category_name:
            Category.objects.create(name=category_name)
            return redirect('blog_requests')  # Reload page to see the changes
        else:
            return render(request, 'admin/base.html', {
                'error_message': 'Category name cannot be empty.',
            })
    # Get the current page number from the request GET parameters
    
    return render(request,'admin/base.html',{'page_obj':page_obj,'all':full})


def post_request(request):
    filter_option = request.GET.get('filter', 'all')  # Default to 'all'

    if filter_option == 'accepted':
        posts = Post.objects.filter(is_approved=True)
    elif filter_option == 'pending':
        posts = Post.objects.filter(is_approved=False)
    else:
        posts = Post.objects.all()
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number) 
    return render(request,'admin/post_request.html',{'page_obj':page_obj,'filter_option': filter_option})

def approve_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    post.is_approved = True
    post.save()
    return redirect('post_request')

def delete_category(request, id):
    category = Category.objects.get(id=id)
    category.delete()
    return redirect("blog_requests")
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

def accept_request(request, id):
    blog = get_object_or_404(blog_request, id=id)

    if blog.status:  # If the request is pending
        blog.status = False  # Mark as accepted
        blog.save()

        # Generate the registration link with uid and token
        uid = urlsafe_base64_encode(force_bytes(blog.id))
        registration_link = request.build_absolute_uri(
        reverse('users-sign-up', kwargs={'uid': uid})
        )

        # Send an email to the user
        try:
            send_mail(
                subject='Account Activation Request Accepted',
                message=(
                    f'Dear {blog.name},\n\n'
                    f'Your account activation request has been accepted. '
                    f'Please complete your registration using the link below:\n\n{registration_link}\n\n'
                    f'Thank you.'
                ),
                from_email='nikhilravindren01@gmail.com',  # Replace with your valid email
                recipient_list=[blog.mail],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Email sending failed: {e}")
    else:
        blog.status = True  # Toggle back to pending (if necessary)
        blog.save()

    return redirect('blog_requests')
