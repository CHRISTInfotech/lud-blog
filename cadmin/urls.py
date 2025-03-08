from django.urls import path
from .import views
from django.contrib.auth import views as auth_view
from .views import blog_requests,accept_request,delete_category,post_request

urlpatterns = [
    path('',blog_requests,name='blog_requests'),
    path('accept_request/<int:id>/',accept_request,name='accept_request'),
    path('delete_category/<int:id>/',delete_category,name='delete_category'),
    path('post_request',post_request,name='post_request'),
    path('posts/approve/<int:post_id>/', views.approve_post, name='approve_post'),
    path('edit_profile_admin/',views.edit_profile_admin,name='edit_profile_admin'),
    path('invite_user/',views.invite_user,name='invite_user'),
    path('manage_user/',views.manage_user,name='manage_user'),
    path('blog_detail_published',views.blog_detail_published,name='blog_detail_published'),
    path('view_invited_user/',views.view_invited_user,name='view_invited_user'),
    path("toggle-user/<int:user_id>/", views.toggle_user_status, name="toggle_user_status"),
    path('admin_edit_blog/<int:blog_id>/', views.admin_edit_blog, name='admin_edit_blog'),
    path('admin/categories/', views.manage_categories, name='admin_manage_categories'),
    path('admin_chart/',views.admin_chart,name='admin_chart'),
    path('disable-category/<int:category_id>/', views.disable_category, name='admin_disable_category'),
    path('enable-category/<int:category_id>/', views.enable_category, name='admin_enable_category'),
]