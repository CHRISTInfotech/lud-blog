from django.urls import path
from .import views
from django.contrib.auth import views as auth_view


urlpatterns = [
    path('logout/', views.logout_view, name='logout'),
    path("login/", views.request_otp, name="request_otp"),
    path("verify/", views.verify_otp, name="verify_otp"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("create_post/", views.create_post, name="create_post"),
    path('blog/<uuid:pk>/', views.blog_detail, name='blog_detail'),
    path("user_blog_update/", views.user_blog_update, name="user_blog_update"),
    path('user_edit_blog/<uuid:blog_id>/', views.user_edit_blog, name='user_edit_blog'),
    path('blog/like/<uuid:pk>/', views.like_blog, name='like_blog'),
    path('blog/dislike/<uuid:pk>/', views.dislike_blog, name='dislike_blog'),
    path('profile/<int:pk>/', views.user_profile, name='user_profile'),
    path('blog_detail_while_editing/<uuid:pk>/', views.blog_detail_while_editing, name='blog_detail_while_editing'),
]
