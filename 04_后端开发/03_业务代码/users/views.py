from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate
from .models import User, Role, Permission, Menu
from .serializers import UserSerializer, UserCreateSerializer, RoleSerializer, MenuSerializer
from .authentication import generate_token, refresh_access_token


class UserViewSet(viewsets.ModelViewSet):
    """用户管理视图"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['username', 'phone', 'email']
    filterset_fields = ['status', 'gender']

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.filter(is_superuser=False)

    @action(detail=False, methods=['post'])
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


class MenuViewSet(viewsets.ModelViewSet):
    """菜单管理视图"""
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Menu.objects.filter(visible=True)
        user = self.request.user
        permissions = user.roles.filter(status=True).values_list('permissions__code', flat=True)
        return Menu.objects.filter(visible=True, permission__in=permissions).distinct()

    @action(detail=False, methods=['get'])
    def tree(self, request):
        """获取菜单树"""
        menus = self.get_queryset()
        root_menus = menus.filter(parent__isnull=True)
        serializer = MenuSerializer(root_menus, many=True)
        return Response(serializer.data)


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """权限管理视图"""
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [permissions.IsAuthenticated]
    search_fields = ['name', 'code']