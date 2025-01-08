from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile_view, name='profile_page'),
    path('edit/', views.edit_profile, name='edit_profile'),
]
