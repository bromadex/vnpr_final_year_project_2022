from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import SignUpView, LoginView, logout_view, UserProfileView

app_name = 'accounts'

urlpatterns = [
    path("login/", LoginView.as_view(), name='login_page'),
    path("signup/", SignUpView.as_view(), name='signup_page'),
    path("logout/", logout_view, name='logout'),
    path("api-token-auth/", obtain_auth_token, name='api_token_auth'),
    path("user/", UserProfileView.as_view(), name='user_profile'),
]
