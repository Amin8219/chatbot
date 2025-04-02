# authentication/urls.py
from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import signup_view, login_view, forgot_password_view, verify_code_view, reset_password_view

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('forgot-password/', forgot_password_view, name='forgot_password'),
    path('verify-code/', verify_code_view, name='verify_code'),
    path('reset-password/', reset_password_view, name='reset_password'),
]