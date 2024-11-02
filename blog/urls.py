from django.urls import path
from . import views

urlpatterns = [
    path('blog/', views.index, name='blog-index'),
    path('', views.home, name='blog-home'),
    path('category/<int:category_id>/', views.category_posts, name='category-posts'),
    path('post_detail/<int:pk>/', views.post_detail, name='blog-post-detail'),
    path('post_edit/<int:pk>/', views.post_edit, name='blog-post-edit'),
    path('post_delete/<int:pk>/', views.post_delete, name='blog-post-delete'),
    path('post/about/<int:pk>/', views.about_post, name='blog-about-post'),
    path('create_post/', views.create_post, name='blog-create_post'),  # No change here
    path('post/<int:pk>/archive/', views.archive_post, name='blog-post-archive'),  # Archive URL
    path('post/<int:pk>/unarchive/', views.unarchive_post, name='blog-post-unarchive'),
    path('archived/', views.archived_posts, name='archived-posts'),  # Archived posts URL
    path('approve-post/<int:post_id>/', views.approve_post, name='approve_post'),  # Corrected single post approval URL
]
