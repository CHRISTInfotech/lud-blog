from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from cadmin.models import blog_request

@login_required
def index(request):
    posts = Post.objects.filter(is_archived=False,author=request.user)  # Show only active posts
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.user
        category = request.POST.get('category')
        instance = Post(title=title,content=content,author=author,category=category)
        instance.save()
        return redirect('blog-index')
        # if form.is_valid():
        #     instance = form.save(commit=False)
        #     instance.author = request.user
        #     instance.save()
        #     return redirect('blog-index')

    context = {
        'posts': posts,
    }
    return render(request, 'blog/index.html', context)

@login_required
def archive_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user == post.author:
        post.is_archived = True
        post.save()
    return redirect('blog-index')

@login_required
def archived_posts(request):
    posts = Post.objects.filter(is_archived=True)  # Show only archived posts
    paginator = Paginator(posts, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
    }
    return render(request, 'blog/archived_posts.html', context)

@login_required
def unarchive_post(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.user == post.author:
        post.is_archived = False
        post.save()
    return redirect('archived-posts')

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        instance = Comment(user=request.user,post=post,content=content)
        instance.save()
        return redirect('blog-post-detail', pk=post.id)
        # c_form = CommentForm(request.POST)
        # if c_form.is_valid():
        #     instance = c_form.save(commit=False)
        #     instance.user = request.user
        #     instance.post = post
        #     instance.save()
        #     return redirect('blog-post-detail', pk=post.id)

    context = {
        'post': post,
    }
    return render(request, 'blog/post_detail.html', context)

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, id=pk)
    category = Category.objects.all()
    if request.method == 'POST':
        post.title = request.POST.get('title')
        post.content = request.POST.get('content')
        post.author = request.user
        cat = request.POST.get('category')
        post.category = Category.objects.get(id=cat)
        post.save()
        return redirect('blog-index')

    context = {
        'post': post,
        'all':category,
    }
    return render(request, 'blog/post_edit.html', context)

@login_required
def post_delete(request, pk):
    post = get_object_or_404(Post, id=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('blog-index')

    context = {
        'post': post,
    }
    return render(request, 'blog/post_delete.html', context)

def home(request):
    categories = Category.objects.all()
    approved_posts = Post.objects.filter(is_approved=True,is_archived=False).order_by('-date_created')
    paginator = Paginator(approved_posts, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'categories': categories,
        'page_obj': page_obj,
    }
    return render(request, 'blog/home.html', context)


def about_post(request, pk):
    post = get_object_or_404(Post, id=pk)

    context = {
        'post': post,
    }
    return render(request, 'blog/about_post.html', context)

@login_required
def create_post(request):
    full = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        author = request.user
        category_id = request.POST.get('category')
        category = Category.objects.get(id=category_id)
        instance = Post(title=title,content=content,author=author,category=category)
        instance.save()
        return redirect('blog-index')
        
    #     form = PostForm(request.POST)
    #     if form.is_valid():
    #         instance = form.save(commit=False)
    #         instance.author = request.user
    #         instance.save()
    #         return redirect('blog-index')
    # else:
    #     form = PostForm()
    return render(request, 'blog/create_post.html',{'all':full})

def category_posts(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    categories = Category.objects.all()
    posts = Post.objects.filter(category=category, is_approved=True,is_archived=False).order_by('-date_created')
    paginator = Paginator(posts, 5)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'category': category,
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'blog/category_posts.html', context)

@login_required
def approve_posts(request):
    if not request.user.is_superuser:
        return redirect('blog-home')  # Only allow admin access

@login_required
def approve_post(request, post_id):
    if not request.user.is_superuser:
        return redirect('blog-home')

    post = get_object_or_404(Post, id=post_id)
    post.is_approved = True
    post.save()
    return redirect('approve_posts')
