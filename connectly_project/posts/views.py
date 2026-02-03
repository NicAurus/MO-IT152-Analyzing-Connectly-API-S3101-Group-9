import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password, make_password
from .models import User, Post
from .factories import PostFactory
from .logger import LoggerSingleton
from .security import TokenService, require_token


def _validate_required_fields(data, required_fields):
    missing = [field for field in required_fields if not data.get(field)]
    return missing


@require_token
def get_users(request):
    logger = LoggerSingleton.get_logger()
    try:
        users = list(User.objects.values('id', 'username', 'email', 'created_at'))
        logger.info("Fetched users list")
        return JsonResponse(users, safe=False)
    except Exception as e:
        logger.error("Failed to fetch users: %s", e)
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def create_user(request):
    logger = LoggerSingleton.get_logger()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            missing = _validate_required_fields(data, ["username", "email", "password"])
            if missing:
                return JsonResponse(
                    {"error": f"Missing required fields: {', '.join(missing)}"},
                    status=400,
                )
            user = User.objects.create(
                username=data['username'],
                email=data['email'],
                password_hash=make_password(data['password']),
            )
            logger.info("Created user %s", user.username)
            return JsonResponse(
                {'id': user.id, 'message': 'User created successfully'},
                status=201
            )
        except Exception as e:
            logger.error("Failed to create user: %s", e)
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def login(request):
    logger = LoggerSingleton.get_logger()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            missing = _validate_required_fields(data, ["username", "password"])
            if missing:
                return JsonResponse(
                    {"error": f"Missing required fields: {', '.join(missing)}"},
                    status=400,
                )
            user = User.objects.get(username=data["username"])
            if not check_password(data["password"], user.password_hash):
                logger.warning("Invalid login attempt for %s", user.username)
                return JsonResponse({"error": "Invalid credentials"}, status=401)
            user.auth_token = TokenService.generate_token()
            user.save(update_fields=["auth_token"])
            logger.info("Issued token for %s", user.username)
            return JsonResponse({"token": user.auth_token}, status=200)
        except User.DoesNotExist:
            logger.warning("Login attempt for unknown user")
            return JsonResponse({"error": "Invalid credentials"}, status=401)
        except Exception as e:
            logger.error("Failed to login: %s", e)
            return JsonResponse({"error": str(e)}, status=400)


@require_token
def get_posts(request):
    logger = LoggerSingleton.get_logger()
    try:
        posts = list(Post.objects.values('id', 'content', 'author', 'created_at'))
        logger.info("Fetched posts list")
        return JsonResponse(posts, safe=False)
    except Exception as e:
        logger.error("Failed to fetch posts: %s", e)
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_token
def create_post(request):
    logger = LoggerSingleton.get_logger()
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            missing = _validate_required_fields(data, ["author", "content"])
            if missing:
                return JsonResponse(
                    {"error": f"Missing required fields: {', '.join(missing)}"},
                    status=400,
                )
            if len(data["content"].strip()) < 3:
                return JsonResponse(
                    {"error": "Content must be at least 3 characters long."},
                    status=400,
                )
            if request.authenticated_user.id != data["author"]:
                logger.warning("Forbidden post creation attempt by user %s", request.authenticated_user.id)
                return JsonResponse({"error": "Forbidden"}, status=403)
            author = User.objects.get(id=data['author'])
            post = PostFactory.create_post(author=author, content=data['content'])
            logger.info("Created post %s by user %s", post.id, author.id)
            return JsonResponse(
                {'id': post.id, 'message': 'Post created successfully'},
                status=201
            )
        except User.DoesNotExist:
            return JsonResponse({'error': 'Author not found'}, status=404)
        except Exception as e:
            logger.error("Failed to create post: %s", e)
            return JsonResponse({'error': str(e)}, status=400)
