from django.core.paginator import Paginator
from django.core.paginator import Paginator
from django.shortcuts import render
from users.models import Blog,Category
from django.shortcuts import render
from django.core.paginator import Paginator
from users.models import Blog, Category

def home(request):
    search_query = request.GET.get('search', '').strip()  # Get search term
    category_filter = request.GET.get('category', '').strip()  # Get selected category

    # Get accepted posts that belong to active categories
    accepted_posts = Blog.objects.filter(status='accepted', category__is_active=True).order_by('-created_at')

    # Apply search filter
    if search_query:
        accepted_posts = accepted_posts.filter(title__icontains=search_query)

    # Apply category filter
    if category_filter and category_filter.lower() != 'all':
        accepted_posts = accepted_posts.filter(category__name__iexact=category_filter)

    # Paginate with 9 posts per page (3x3 grid)
    paginator = Paginator(accepted_posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get all active categories
    categories = Category.objects.filter(is_active=True)

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category_filter,
    }
    
    return render(request, 'blog/home.html', context)
