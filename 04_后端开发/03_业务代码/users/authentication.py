import jwt
import time
from datetime import datetime, timedelta
from rest_framework import authentication, exceptions
from django.conf import settings
from .models import User


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = ''
        if hasattr(request, 'headers'):
            auth_header = request.headers.get('Authorization', '') or request.headers.get('authorization', '')
        if not auth_header:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '') or request.META.get('Authorization', '')

        token = auth_header.replace('Bearer ', '').strip()
        if not token:
            return None

        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token已过期')
        except jwt.InvalidTokenError:
            raise exceptions.AuthenticationFailed('Token无效')

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('用户不存在')

        if user.status == 'inactive':
            raise exceptions.AuthenticationFailed('用户已被禁用')

        return (user, token)


def generate_token(user_id, username):
    """生成JWT Token"""
    now = datetime.utcnow()
    access_exp = now + timedelta(seconds=settings.JWT_ACCESS_TOKEN_LIFETIME)
    refresh_exp = now + timedelta(seconds=settings.JWT_REFRESH_TOKEN_LIFETIME)

    access_payload = {
        'user_id': user_id,
        'username': username,
        'type': 'access',
        'exp': access_exp,
        'iat': now
    }

    refresh_payload = {
        'user_id': user_id,
        'username': username,
        'type': 'refresh',
        'exp': refresh_exp,
        'iat': now
    }

    access_token = jwt.encode(access_payload, settings.JWT_SECRET_KEY, algorithm='HS256')
    refresh_token = jwt.encode(refresh_payload, settings.JWT_SECRET_KEY, algorithm='HS256')

    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'expires_in': settings.JWT_ACCESS_TOKEN_LIFETIME
    }


def verify_token(token):
    """验证Token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def refresh_access_token(refresh_token):
    """刷新Access Token"""
    payload = verify_token(refresh_token)
    if not payload or payload.get('type') != 'refresh':
        return None

    user = User.objects.get(id=payload['user_id'])
    if user.status == 'inactive':
        return None

    return generate_token(user.id, user.username)
