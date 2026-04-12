from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

# 导入Prometheus监控
from prometheus_client import Counter, Histogram, Summary
import time

# 创建监控指标
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP Requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP Request Latency', ['method', 'endpoint'])
REQUEST_TIME = Summary('request_processing_seconds', 'Time spent processing request')

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    return Response({
        'message': 'EduAdmin API',
        'version': '1.0',
        'endpoints': {
            'users': '/api/users/',
            'edu': '/api/edu/',
            'classroom': '/api/classroom/',
            'exam': '/api/exam/',
            'finance': '/api/finance/',
        }
    })

# 添加Prometheus监控端点
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from django.http import HttpResponse

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def metrics(request):
    """Prometheus监控端点"""
    return HttpResponse(generate_latest(), content_type=CONTENT_TYPE_LATEST)

# 添加Swagger文档
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

SchemaView = get_schema_view(
    openapi.Info(
        title="EduAdmin API",
        default_version='v1',
        description="教育管理系统API文档",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root),
    path('api/users/', include('users.urls')),
    path('api/edu/', include('edu.urls')),
    path('api/classroom/', include('classroom.urls')),
    path('api/exam/', include('exam.urls')),
    path('api/finance/', include('finance.urls')),
    # Prometheus监控端点
    path('metrics/', metrics),
    # Swagger文档
    path('swagger/', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)