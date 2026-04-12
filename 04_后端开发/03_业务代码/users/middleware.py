from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .authentication import verify_token
from .models import User, Permission


class PermissionMiddleware(MiddlewareMixin):
    """权限检查中间件"""
    
    def process_request(self, request):
        # 跳过登录、注册等不需要认证的路径
        if request.path in ['/api/users/login', '/api/users/register', '/api/users/reset_password', '/api/users/send_sms_code']:
            return None
        
        # 跳过静态文件和媒体文件
        if request.path.startswith('/static/') or request.path.startswith('/media/'):
            return None
        
        # 从请求头获取token
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({'error': '缺少认证token'}, status=401)
        
        token = auth_header.split(' ')[1]
        
        # 验证token
        payload = verify_token(token)
        if not payload:
            return JsonResponse({'error': 'token无效或已过期'}, status=401)
        
        user_id = payload.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'token格式错误'}, status=401)
        
        # 获取用户信息
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=401)
        
        # 设置request.user
        request.user = user
        
        # 获取用户所有权限
        user_permissions = set()
        for role in user.roles.filter(status=True):
            for perm in role.permissions.all():
                user_permissions.add(perm.code)
        
        # 保存用户权限到请求对象
        request.user_permissions = user_permissions
        
        # 管理员用户跳过权限检查
        if user.is_superuser:
            # 即使是管理员也要设置user_permissions
            return None
        
        # 检查API权限
        api_path = request.path
        method = request.method
        
        # 查找匹配的权限
        permission = Permission.objects.filter(
            api_path=api_path,
            method=method
        ).first()
        
        # 如果API需要权限但用户没有，则拒绝访问
        if permission and permission.code not in user_permissions:
            return JsonResponse({'error': '权限不足'}, status=403)
        
        return None


class OperationLogMiddleware(MiddlewareMixin):
    """操作日志中间件"""
    
    def process_request(self, request):
        # 记录请求开始时间
        request.start_time = None
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            import time
            request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # 记录操作日志
        if not request.path.startswith('/static/') and not request.path.startswith('/media/'):
            from .models import OperationLog
            import time
            import json
            
            duration = 0
            if hasattr(request, 'start_time') and request.start_time:
                duration = int((time.time() - request.start_time) * 1000)
            
            try:
                body = json.dumps(request.body.decode('utf-8')[:1000])
            except:
                body = ''
            
            try:
                response_content = response.content.decode('utf-8')[:1000]
            except:
                response_content = ''
            
            # 记录日志
            user = getattr(request, 'user', None)
            # 确保user不是AnonymousUser
            if user and hasattr(user, 'is_anonymous') and user.is_anonymous:
                user = None
                username = '匿名'
            else:
                username = user.username if user else '匿名'
            
            OperationLog.objects.create(
                user=user,
                username=username,
                method=request.method,
                path=request.path,
                body=body,
                response=response_content,
                ip=request.META.get('REMOTE_ADDR'),
                duration=duration
            )
        
        return response