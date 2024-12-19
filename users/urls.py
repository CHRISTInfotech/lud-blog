from django.urls import path
from .import views
from django.contrib.auth import views as auth_view
from .views import logout_view,user_user_login,send_request

urlpatterns = [
    path('register/<str:uid>/', views.sign_up, name='users-sign-up'),
    path('profile/', views.profile, name='users-profile'),
    path('logout/', logout_view, name='logout'),
    path('user_user_login/', user_user_login, name='user_user_login'),
    path('send_request/', send_request, name='send_request'),
    
]
