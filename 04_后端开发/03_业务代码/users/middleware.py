from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .authentication import verify_token
from .models import User, Permission


class PermissionMiddleware(MiddlewareMixin):
    """权限检查中间件"""
    
    # 不需要认证的路径
    EXEMPT_PATHS = [
        '/api/users/login',
        '/api/users/register', 
        '/api/users/reset_password',
        '/api/users/send_sms_code',
    ]
    
    def process_request(self, request):
        # 跳过不需要认证的路径
        path = request.path
        if path in self.EXEMPT_PATHS:
            return None
        
        # 跳过静态文件和媒体文件
        if path.startswith('/static/') or path.startswith('/media/'):
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
            user = User.objects.select_related().prefetch_related('roles__permissions').get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({'error': '用户不存在'}, status=401)
        
        # 设置request.user
        request.user = user
        
        # 获取用户所有权限编码
        user_permissions = set()
        for role in user.roles.filter(status=True):
            for perm in role.permissions.all():
                user_permissions.add(perm.code)
        
        # 保存用户权限到请求对象
        request.user_permissions = user_permissions
        
        # 超级管理员跳过权限检查
        if user.is_superuser:
            return None
        
        # 检查API权限
        method = request.method
        
        # 根据API路径和方法确定需要的权限
        required_permission = self._get_required_permission(path, method)
        
        if required_permission and required_permission not in user_permissions:
            return JsonResponse({'error': f'权限不足，需要权限: {required_permission}'}, status=403)
        
        return None
    
    def _get_required_permission(self, path, method):
        """根据API路径和方法确定需要的权限"""
        # 用户管理
        if path.startswith('/api/users/'):
            if path == '/api/users/roles/' and method == 'GET':
                return 'role_management'
            if path == '/api/users/menus/' and method == 'GET':
                return 'menu_management'
            if path == '/api/users/permissions/' and method == 'GET':
                return 'permission_management'
            if path == '/api/users/operation-logs/' and method == 'GET':
                return 'log_management'
            if path == '/api/users/notifications/' and method == 'GET':
                return 'notification_management'
            if path == '/api/users/' and method == 'GET':
                return 'user_management'
            if path == '/api/users/' and method == 'POST':
                return 'user_create'
            if path == '/api/users/' and method == 'PUT':
                return 'user_edit'
            if path == '/api/users/' and method == 'DELETE':
                return 'user_delete'
        
        # 教务管理
        if path.startswith('/api/edu/students/'):
            if method == 'GET':
                return 'student_management'
            if method == 'POST':
                return 'student_create'
            if method == 'PUT':
                return 'student_edit'
            if method == 'DELETE':
                return 'student_delete'
        
        if path.startswith('/api/edu/teachers/'):
            if method == 'GET':
                return 'teacher_management'
            if method == 'POST':
                return 'teacher_create'
            if method == 'PUT':
                return 'teacher_edit'
            if method == 'DELETE':
                return 'teacher_delete'
        
        if path.startswith('/api/edu/courses/'):
            if method == 'GET':
                return 'course_management'
            if method == 'POST':
                return 'course_create'
            if method == 'PUT':
                return 'course_edit'
            if method == 'DELETE':
                return 'course_delete'
        
        if path.startswith('/api/edu/classes/'):
            if method == 'GET':
                return 'class_management'
            if method == 'POST':
                return 'class_create'
            if method == 'PUT':
                return 'class_edit'
            if method == 'DELETE':
                return 'class_delete'
        
        if path.startswith('/api/edu/schedules/'):
            if method == 'GET':
                return 'schedule_management'
            if method == 'POST':
                return 'schedule_create'
            if method == 'PUT':
                return 'schedule_edit'
            if method == 'DELETE':
                return 'schedule_delete'
        
        if path.startswith('/api/edu/reschedules/'):
            if method == 'GET':
                return 'reschedule_management'
        
        if path.startswith('/api/edu/leaves/'):
            if method == 'GET':
                return 'leave_management'
        
        if path.startswith('/api/edu/student-hours/'):
            if method == 'GET':
                return 'hours_account_management'
        
        if path.startswith('/api/edu/hours-flows/'):
            if method == 'GET':
                return 'hours_flow_view'
        
        # 考试管理
        if path.startswith('/api/exam/questions/'):
            if method == 'GET':
                return 'question_management'
            if method == 'POST':
                return 'question_create'
            if method == 'PUT':
                return 'question_edit'
            if method == 'DELETE':
                return 'question_delete'
            if '/import/' in path and method == 'POST':
                return 'question_import'
            if '/export/' in path and method == 'GET':
                return 'question_export'
        
        if path.startswith('/api/exam/papers/'):
            if method == 'GET':
                return 'paper_management'
            if method == 'POST':
                return 'paper_create'
            if method == 'PUT':
                return 'paper_edit'
            if method == 'DELETE':
                return 'paper_delete'
        
        if path.startswith('/api/exam/exams/'):
            if method == 'GET':
                return 'exam_management'
            if method == 'POST':
                return 'exam_create'
            if method == 'PUT':
                return 'exam_edit'
            if method == 'DELETE':
                return 'exam_delete'
            if '/publish/' in path and method == 'POST':
                return 'exam_publish'
            if '/correct/' in path and method == 'PATCH':
                return 'score_correct'
        
        if path.startswith('/api/exam/scores/'):
            if method == 'GET':
                return 'score_view'
        
        # 财务管理
        if path.startswith('/api/finance/orders/'):
            if method == 'GET':
                return 'order_management'
            if method == 'POST':
                return 'order_create'
            if method == 'PUT':
                return 'order_edit'
            if method == 'DELETE':
                return 'order_delete'
            if '/pay/' in path and method == 'POST':
                return 'order_pay'
        
        if path.startswith('/api/finance/refunds/'):
            if method == 'GET':
                return 'refund_management'
            if method == 'POST':
                return 'refund_create'
            if method == 'PATCH':
                return 'refund_approve'
        
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
            
            # 检查user是否为User实例
            user = getattr(request, 'user', None)
            if user and hasattr(user, 'is_anonymous') and user.is_anonymous:
                user = None
                username = '匿名'
            elif user:
                username = user.username if hasattr(user, 'username') else '未知'
            else:
                username = '匿名'
            
            # 记录日志
            try:
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
            except:
                pass
        
        return response