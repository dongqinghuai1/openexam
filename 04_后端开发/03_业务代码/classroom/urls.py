from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MeetingRoomViewSet, MeetingRecordViewSet, RecordingTaskViewSet,
    PlaybackFileViewSet, ClassNoteViewSet
)

router = DefaultRouter()
router.register(r'meeting_rooms', MeetingRoomViewSet, basename='meeting-room')
router.register(r'records', MeetingRecordViewSet, basename='meeting-record')
router.register(r'recordings', RecordingTaskViewSet, basename='recording-task')
router.register(r'playbacks', PlaybackFileViewSet, basename='playback')
router.register(r'notes', ClassNoteViewSet, basename='class-note')

urlpatterns = [
    path('', include(router.urls)),
    path('meeting_rooms/create_meeting/', MeetingRoomViewSet.as_view({'post': 'create_meeting'}), name='meeting-room-create-meeting'),
    path('meeting_rooms/<int:pk>/get_token/', MeetingRoomViewSet.as_view({'get': 'get_token'}), name='meeting-room-get-token'),
    path('meeting_rooms/<int:pk>/start_meeting/', MeetingRoomViewSet.as_view({'post': 'start_meeting'}), name='meeting-room-start'),
    path('meeting_rooms/<int:pk>/end_meeting/', MeetingRoomViewSet.as_view({'post': 'end_meeting'}), name='meeting-room-end'),
]
