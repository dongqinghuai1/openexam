from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SubjectViewSet, CourseViewSet, ChapterViewSet, StudentViewSet, TeacherViewSet,
    EduClassViewSet, ScheduleViewSet, RescheduleRecordViewSet, LeaveRecordViewSet,
    StudentHoursAccountViewSet, HoursFlowViewSet
)

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'teachers', TeacherViewSet, basename='teacher')
router.register(r'classes', EduClassViewSet, basename='class')
router.register(r'schedules', ScheduleViewSet, basename='schedule')
router.register(r'reschedules', RescheduleRecordViewSet, basename='reschedule')
router.register(r'leaves', LeaveRecordViewSet, basename='leave')
router.register(r'hours/accounts', StudentHoursAccountViewSet, basename='hours-account')
router.register(r'hours/flows', HoursFlowViewSet, basename='hours-flow')

urlpatterns = [
    path('', include(router.urls)),
]