from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, MenuViewSet, PermissionViewSet, OperationLogViewSet, NotificationViewSet, DashboardView, LoginView

router = DefaultRouter(trailing_slash=False)
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('login', LoginView.as_view(), name='login-no-slash'),
    path('', include(router.urls)),
    path('roles/', RoleViewSet.as_view({'get': 'list', 'post': 'create'}), name='role-list'),
    path('roles/<int:pk>/', RoleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='role-detail'),
    path('menus/', MenuViewSet.as_view({'get': 'list', 'post': 'create'}), name='menu-list'),
    path('menus/tree/', MenuViewSet.as_view({'get': 'tree'}), name='menu-tree'),
    path('menus/all/', MenuViewSet.as_view({'get': 'all'}), name='menu-all'),
    path('menus/<int:pk>/', MenuViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='menu-detail'),
    path('permissions/', PermissionViewSet.as_view({'get': 'list'}), name='permission-list'),
    path('operation-logs/', OperationLogViewSet.as_view({'get': 'list'}), name='operation-log-list'),
    path('notifications/', NotificationViewSet.as_view({'get': 'list', 'post': 'create'}), name='notification-list'),
    path('notifications/<int:pk>/', NotificationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='notification-detail'),
    path('notifications/<int:pk>/publish/', NotificationViewSet.as_view({'post': 'publish'}), name='notification-publish'),
    path('dashboard/', DashboardView.as_view(), name='dashboard-data'),
]
