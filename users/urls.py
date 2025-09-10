from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication URLs
    path('register/', views.UserRegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    
    # Profile management
    path('profile/', views.profile_view, name='profile'),
    
    # Alternative function-based registration (commented out)
    # path('register/', views.register_view, name='register'),
]