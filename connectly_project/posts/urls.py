from django.urls import path
from . import views

urlpatterns = [
    path('users/', views.get_users),
    path('users/create/', views.create_user),
    path('posts/', views.get_posts),
    path('posts/create/', views.create_post),
]
