import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsPostAuthor
from .models import User, Post, Comment
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import Group, User
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from rest_framework import status




def get_users(request):
    try:
        users = list(User.objects.values('id', 'username', 'email', 'created_at'))
        return JsonResponse(users, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = User.objects.create(
                username=data['username'],
                email=data['email']
            )
            return JsonResponse(
                {'id': user.id, 'message': 'User created successfully'},
                status=201
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


def get_posts(request):
    try:
        posts = list(Post.objects.values('id', 'content', 'author', 'created_at'))
        return JsonResponse(posts, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_post(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            author = User.objects.get(id=data['author'])
            post = Post.objects.create(
                content=data['content'],
                author=author
            )
            return JsonResponse(
                {'id': post.id, 'message': 'Post created successfully'},
                status=201
            )
        except User.DoesNotExist:
            return JsonResponse({'error': 'Author not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
        

def get_comments(request):
    try:
        comments = list(Comment.objects.values(
            'id', 'post', 'author', 'content', 'created_at'
        ))
        return JsonResponse(comments, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
        

def get_comments(request):
    try:
        comments = list(Comment.objects.values(
            'id', 'post', 'author', 'content', 'created_at'
        ))
        return JsonResponse(comments, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_comment(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            post = Post.objects.get(id=data['post'])
            author = User.objects.get(id=data['author'])
            comment = Comment.objects.create(
                post=post,
                author=author,
                content=data['content']
            )
            return JsonResponse(
                {'id': comment.id, 'message': 'Comment created successfully'},
                status=201
            )
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post not found'}, status=404)
        except User.DoesNotExist:
            return JsonResponse({'error': 'Author not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


class PostDetailView(APIView):
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(request, post)
        return Response({"content": post.content})
    
    from rest_framework.authentication import TokenAuthentication

class ProtectedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Authenticated!"})


admin_group, created = Group.objects.get_or_create(name="Admin")
regular_group, created = Group.objects.get_or_create(name="Regular")

user = User.objects.get(username="admin_user")
user.groups.add(admin_group)

user2 = User.objects.get(username="john")
user2.groups.add(regular_group)


class PostCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
    
        data = request.data.copy()  
        data['author'] = request.user.id  

        serializer = PostSerializer(data=data)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentCreateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data['author'] = request.user.id 
        if 'post' not in data:
            return Response({"error": "Post ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListPostsView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)