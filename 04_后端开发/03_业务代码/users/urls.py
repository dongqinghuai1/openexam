from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, RoleViewSet, MenuViewSet, PermissionViewSet

router = DefaultRouter()
router.register(r'', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('roles/', RoleViewSet.as_view({'get': 'list', 'post': 'create'}), name='role-list'),
    path('roles/<int:pk>/', RoleViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='role-detail'),
    path('menus/', MenuViewSet.as_view({'get': 'list', 'post': 'create'}), name='menu-list'),
    path('menus/tree/', MenuViewSet.as_view({'get': 'tree'}), name='menu-tree'),
    path('menus/<int:pk>/', MenuViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='menu-detail'),
    path('permissions/', PermissionViewSet.as_view({'get': 'list'}), name='permission-list'),
]