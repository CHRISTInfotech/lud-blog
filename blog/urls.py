from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='blog-home'),
    path('user_workflow/',views.user_workflow,name='user_workflow'),
    path('admin_workflow/',views.admin_workflow,name='admin_workflow'),
]
