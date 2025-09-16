from django.urls import path
from django.contrib.auth import views as auth_views
from . import views  # your signup view lives here

app_name = 'accounts'

urlpatterns = [
    path(
        'login/',
        auth_views.LoginView.as_view(template_name='accounts/login.html'),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='home:index'),
        name='logout',
    ),
    path('signup/', views.signup, name='signup'),
]
