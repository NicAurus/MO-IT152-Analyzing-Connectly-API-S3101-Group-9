from .models import Post, Comment
from django.contrib.auth.models import User
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email'] 

class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True) 
    post = serializers.PrimaryKeyRelatedField(queryset=Post.objects.all()) 

    class Meta:
        model = Comment
        fields = ['id', 'post', 'content', 'author', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at']
