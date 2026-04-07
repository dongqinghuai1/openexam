from django.urls import path, include

urlpatterns = [
    path('api/users/', include('users.urls')),
    path('api/edu/', include('edu.urls')),
    path('api/classroom/', include('classroom.urls')),
    path('api/exam/', include('exam.urls')),
    path('api/finance/', include('finance.urls')),
]