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
    
]