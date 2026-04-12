from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from functools import wraps


def permission_required(permission_codes):
    """权限检查装饰器
    
    Args:
        permission_codes: 权限编码列表或单个权限编码
    """
    if isinstance(permission_codes, str):
        permission_codes = [permission_codes]
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # 管理员用户跳过权限检查
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # 获取用户权限
            user_permissions = getattr(request, 'user_permissions', set())
            
            # 检查用户是否有所有要求的权限
            for permission_code in permission_codes:
                if permission_code not in user_permissions:
                    return Response({'error': f'缺少权限: {permission_code}'}, status=status.HTTP_403_FORBIDDEN)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


class PermissionRequired:
    """权限检查类，用于ViewSet的permission_classes"""
    
    def __init__(self, permission_codes):
        self.permission_codes = permission_codes if isinstance(permission_codes, list) else [permission_codes]
    
    def has_permission(self, request, view):
        # 管理员用户跳过权限检查
        if request.user.is_superuser:
            return True
        
        # 获取用户权限
        user_permissions = getattr(request, 'user_permissions', set())
        
        # 检查用户是否有所有要求的权限
        for permission_code in self.permission_codes:
            if permission_code not in user_permissions:
                return False
        
        return True
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)