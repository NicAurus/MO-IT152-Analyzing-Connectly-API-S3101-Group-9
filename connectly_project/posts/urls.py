from django.urls import path
from . import views
from .views import CommentCreateView, PostCreateView

urlpatterns = [
    path('users/', views.get_users),
    path('users/create/', views.create_user),
    path('posts/', views.get_posts),
    path('posts/create/', views.create_post),
    path('comments/', views.get_comments),          
    path('comments/create/', views.create_comment), 
    path('create-post/', PostCreateView.as_view(), name='create_post'),
    path('create-comment/', CommentCreateView.as_view(), name='create_comment'),
]
