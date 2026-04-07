from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MeetingRoomViewSet, MeetingRecordViewSet, RecordingTaskViewSet,
    PlaybackFileViewSet, ClassNoteViewSet
)

router = DefaultRouter()
router.register(r'rooms', MeetingRoomViewSet, basename='meeting-room')
router.register(r'records', MeetingRecordViewSet, basename='meeting-record')
router.register(r'recordings', RecordingTaskViewSet, basename='recording-task')
router.register(r'playbacks', PlaybackFileViewSet, basename='playback')
router.register(r'notes', ClassNoteViewSet, basename='class-note')

urlpatterns = [
    path('', include(router.urls)),
]