from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import permissions

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', api_root),
    path('api/users/', include('users.urls')),
    path('api/edu/', include('edu.urls')),
    path('api/classroom/', include('classroom.urls')),
    path('api/exam/', include('exam.urls')),
    path('api/finance/', include('finance.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)