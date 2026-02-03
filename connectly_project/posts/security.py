import secrets
from functools import wraps
from django.http import JsonResponse
from .logger import LoggerSingleton
from .models import User


class TokenService:
    @staticmethod
    def generate_token():
        return secrets.token_hex(32)

    @staticmethod
    def get_user_from_token(token):
        if not token:
            return None
        try:
            return User.objects.get(auth_token=token)
        except User.DoesNotExist:
            return None


def _extract_token(request):
    header = request.headers.get("Authorization", "")
    if header.startswith("Token "):
        return header.split("Token ", 1)[1].strip()
    if header.startswith("Bearer "):
        return header.split("Bearer ", 1)[1].strip()
    return header.strip() or None


def require_token(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        logger = LoggerSingleton.get_logger()
        token = _extract_token(request)
        user = TokenService.get_user_from_token(token)
        if user is None:
            logger.warning("Unauthorized access attempt")
            return JsonResponse({"error": "Unauthorized"}, status=401)
        request.authenticated_user = user
        return view_func(request, *args, **kwargs)

    return _wrapped
