from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_views, name='register'),
    path('profile/', views.profile_views, name='profile'),
    path('profile/edit/', views.edit_profile_views, name='edit_profile'),
    path('login/', views.login_views, name='login'),
    path('logout/', views.logout_views, name='logout')
]