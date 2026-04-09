from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.db.models import Count, Sum
from django.utils import timezone
from .models import User, Role, Permission, Menu, OperationLog, Notification
from .serializers import UserSerializer, UserCreateSerializer, RoleSerializer, MenuSerializer, PermissionSerializer, NotificationSerializer
from .serializers_log import OperationLogSerializer
from .authentication import generate_token, refresh_access_token


class LoginView(APIView):
    """用户登录视图"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.status == 'inactive':
            return Response({'error': '账号已被禁用'}, status=status.HTTP_403_FORBIDDEN)

        token_data = generate_token(user.id, user.username)
        return Response({
            'token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_in': token_data['expires_in'],
            'user': UserSerializer(user).data
        })


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['username', 'phone', 'email']
    filterset_fields = ['status', 'gender']

    def get_permissions(self):
        if self.action == 'login':
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(is_superuser=False)

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def login(self, request):
        """用户登录"""
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)
        if not user:
            return Response({'error': '用户名或密码错误'}, status=status.HTTP_401_UNAUTHORIZED)

        if user.status == 'inactive':
            return Response({'error': '账号已被禁用'}, status=status.HTTP_403_FORBIDDEN)

        token_data = generate_token(user.id, user.username)
        return Response({
            'token': token_data['access_token'],
            'refresh_token': token_data['refresh_token'],
            'expires_in': token_data['expires_in'],
            'user': UserSerializer(user).data
        })

    @action(detail=False, methods=['post'])
    def logout(self, request):
        """用户登出"""
        return Response({'message': '登出成功'})

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        """刷新Token"""
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response({'error': 'refresh_token不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        token_data = refresh_access_token(refresh_token)
        if not token_data:
            return Response({'error': 'refresh_token无效或已过期'}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(token_data)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        user = request.user
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not user.check_password(old_password):
            return Response({'error': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'message': '密码修改成功'})


class RoleViewSet(viewsets.ModelViewSet):
    """角色管理视图"""
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'code']
    filterset_fields = ['status']

    def perform_destroy(self, instance):
        instance.status = False
        instance.save()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class MenuViewSet(viewsets.ModelViewSet):
    """菜单管理视图"""
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Menu.objects.all()
        if self.request.user.is_superuser:
            return queryset.filter(visible=True)
        user = self.request.user
        permissions = user.roles.filter(status=True).values_list('permissions__code', flat=True)
        return queryset.filter(visible=True, permission__in=permissions).distinct()

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        parent_id = request.data.get('parent')
        if parent_id == '' or parent_id is None:
            parent_id = None
        if Menu.objects.filter(name=name, parent_id=parent_id).exists():
            return Response({'error': '该父菜单下已存在同名菜单'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        name = request.data.get('name')
        parent_id = request.data.get('parent')
        if parent_id == '' or parent_id is None:
            parent_id = None
        instance = self.get_object()
        if Menu.objects.exclude(id=instance.id).filter(name=name, parent_id=parent_id).exists():
            return Response({'error': '该父菜单下已存在同名菜单'}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取菜单树（用于表格展示）"""
        menus = Menu.objects.all().order_by('sort', 'id')
        root_menus = menus.filter(parent__isnull=True)
        serializer = MenuSerializer(root_menus, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def all(self, request):
        """获取所有菜单（树形结构，用于下拉框）"""
        menus = Menu.objects.all().order_by('sort', 'id')
        root_menus = menus.filter(parent__isnull=True)
        serializer = MenuSerializer(root_menus, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """权限管理视图"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'code']


class OperationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """操作日志视图"""
    queryset = OperationLog.objects.all()
    serializer_class = OperationLogSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['username', 'method']


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'level', 'target_type']

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        notification = self.get_object()
        notification.status = 'published'
        notification.published_at = timezone.now()
        notification.save(update_fields=['status', 'published_at'])
        return Response(self.get_serializer(notification).data)


class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        from edu.models import Student, Teacher, EduClass, Schedule
        from finance.models import Order

        today = timezone.now().date()
        month_start = today.replace(day=1)

        stats = {
            'studentCount': Student.objects.count(),
            'teacherCount': Teacher.objects.count(),
            'classCount': EduClass.objects.count(),
            'todayRevenue': Order.objects.filter(status='paid', paid_at__date=today).aggregate(total=Sum('final_amount'))['total'] or 0,
        }

        recent_enrollments = list(
            Student.objects.order_by('-created_at').values('name', 'phone')[:5]
        )
        today_schedules = list(
            Schedule.objects.filter(date=today).select_related('edu_class', 'course', 'teacher').order_by('start_time')[:8]
            .values('date', 'start_time', 'end_time', 'edu_class__name', 'course__name', 'teacher__name')
        )
        notifications = list(
            Notification.objects.filter(status='published').values('id', 'title', 'level', 'published_at')[:5]
        )

        return Response({
            'stats': stats,
            'recentEnrollments': [
                {
                    'name': item['name'],
                    'phone': item['phone'],
                    'course': '-',
                    'date': ''
                } for item in recent_enrollments
            ],
            'todaySchedules': [
                {
                    'time': f"{str(item['start_time'])[:5]}-{str(item['end_time'])[:5]}",
                    'className': item['edu_class__name'],
                    'course': item['course__name'],
                    'teacher': item['teacher__name'],
                } for item in today_schedules
            ],
            'notifications': notifications,
            'monthSummary': {
                'paidOrderCount': Order.objects.filter(status='paid', created_at__date__gte=month_start).count(),
                'refundedOrderCount': Order.objects.filter(status='refunded', created_at__date__gte=month_start).count(),
            }
        })
