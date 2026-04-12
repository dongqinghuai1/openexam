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
        '/api/users/me',  # 无斜杠版本
    ]
    
    def process_request(self, request):
        # 处理路径（统一处理带斜杠和不带斜杠的情况）
        path = request.path.rstrip('/')
        
        # 跳过不需要认证的路径
        for exempt_path in self.EXEMPT_PATHS:
            if path == exempt_path or path == exempt_path.rstrip('/'):
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
        
        # 检查用户是否有权访问自己的数据
        if self._check_own_data_permission(path, user):
            return None
        
        # 检查API权限
        required_permission = self._get_required_permission(path)
        
        if required_permission and required_permission not in user_permissions:
            return JsonResponse({'error': f'权限不足，需要权限: {required_permission}'}, status=403)
        
        return None
    
    def _check_own_data_permission(self, path, user):
        """检查用户是否有权访问自己的数据"""
        # 允许访问自己的用户信息
        if path == '/api/users/me':
            return True
        
        # 检查是否是获取单个资源的GET请求
        # 格式: /api/xxx/{id}
        parts = path.strip('/').split('/')
        if len(parts) >= 3 and parts[-1].isdigit():
            resource_id = int(parts[-1])
            resource_type = parts[1]  # students, teachers 等
            
            # 学生查看自己的信息
            if resource_type == 'students':
                if hasattr(user, 'student') and user.student.id == resource_id:
                    return True
                if getattr(user, 'student_id', None) == resource_id:
                    return True
            
            # 教师查看自己的信息
            if resource_type == 'teachers':
                if hasattr(user, 'teacher') and user.teacher.id == resource_id:
                    return True
                if getattr(user, 'teacher_id', None) == resource_id:
                    return True
        
        return False
    
    def _get_required_permission(self, path):
        """根据API路径确定需要的权限"""
        
        # 允许访问自己的用户信息
        if path == '/api/users/me':
            return None
        
        # 系统管理（不包括个人中心）
        if path.startswith('/api/users/') and not path.startswith('/api/users/me'):
            return 'system_management'
        
        # 教务管理
        if path.startswith('/api/edu/students'):
            return 'student_management'
        if path.startswith('/api/edu/teachers'):
            return 'teacher_management'
        if path.startswith('/api/edu/courses'):
            return 'course_management'
        if path.startswith('/api/edu/classes'):
            return 'class_management'
        if path.startswith('/api/edu/schedules'):
            return 'schedule_management'
        if path.startswith('/api/edu/reschedules'):
            return 'reschedule_management'
        if path.startswith('/api/edu/leaves'):
            return 'leave_management'
        if path.startswith('/api/edu/student-hours') or path.startswith('/api/edu/hours-flows'):
            return 'hours_management'
        if path.startswith('/api/edu/classrooms'):
            return 'class_management'  # 教室管理用班级管理权限
        if path.startswith('/api/edu/recording'):
            return 'schedule_management'  # 录播记录用排课权限
        
        # 考试管理
        if path.startswith('/api/exam/questions'):
            return 'question_management'
        if path.startswith('/api/exam/papers'):
            return 'paper_management'
        if path.startswith('/api/exam/exams'):
            return 'exam_management'
        if path.startswith('/api/exam/scores'):
            return 'score_management'
        
        # 财务管理
        if path.startswith('/api/finance/orders'):
            return 'order_management'
        if path.startswith('/api/finance/refunds'):
            return 'refund_management'
        
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