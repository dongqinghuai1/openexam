from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from decimal import Decimal
from edu.models import Schedule, StudentHoursAccount, HoursFlow
from .models import MeetingRoom, MeetingRecord, RecordingTask, PlaybackFile, ClassNote
from .serializers import (
    MeetingRoomSerializer, MeetingRecordSerializer, 
    RecordingTaskSerializer, PlaybackFileSerializer, ClassNoteSerializer
)


class TencentMeetingService:
    """腾讯会议服务（Mock实现）"""

    def create_meeting(self, subject, start_time, end_time, user_id):
        """创建腾讯会议"""
        return {
            'meeting_id': f'meeting_{timezone.now().strftime("%Y%m%d%H%M%S")}',
            'password': '123456',
            'join_url': 'https://meeting.tencent.com/mock-meeting',
            'host_key': '12345678'
        }

    def get_meeting_token(self, meeting_id, user_id, user_name):
        """获取入会Token"""
        return {
            'token': f'token_{meeting_id}_{user_id}',
            'sdk_id': 'mock_sdk_id'
        }


class MeetingRoomViewSet(viewsets.ModelViewSet):
    """会议室视图"""
    queryset = MeetingRoom.objects.all()
    serializer_class = MeetingRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']

    @action(detail=False, methods=['post'])
    def create_meeting(self, request):
        """创建课堂"""
        schedule_id = request.data.get('schedule_id')
        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            return Response({'error': '课次不存在'}, status=status.HTTP_404_NOT_FOUND)

        meeting_service = TencentMeetingService()
        result = meeting_service.create_meeting(
            subject=f"{schedule.edu_class.name} - {schedule.course.name}",
            start_time=schedule.start_time.strftime('%H:%M'),
            end_time=schedule.end_time.strftime('%H:%M'),
            user_id=request.user.id
        )

        meeting_room, created = MeetingRoom.objects.update_or_create(
            schedule=schedule,
            defaults={
                'meeting_id': result['meeting_id'],
                'meeting_password': result['password'],
                'join_url': result['join_url'],
                'host_key': result['host_key'],
                'status': 'pending'
            }
        )

        return Response(MeetingRoomSerializer(meeting_room).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def get_token(self, request, pk=None):
        """获取入会Token"""
        meeting_room = self.get_object()
        user = request.user

        meeting_service = TencentMeetingService()
        result = meeting_service.get_meeting_token(
            meeting_id=meeting_room.meeting_id,
            user_id=user.id,
            user_name=user.username
        )

        return Response({
            'token': result['token'],
            'sdk_id': result['sdk_id'],
            'meeting_id': meeting_room.meeting_id,
            'join_url': meeting_room.join_url,
            'password': meeting_room.meeting_password
        })

    @action(detail=True, methods=['post'])
    def start_meeting(self, request, pk=None):
        """开始会议"""
        meeting_room = self.get_object()
        meeting_room.status = 'ongoing'
        meeting_room.start_time = timezone.now()
        meeting_room.save()

        # 启动录制任务
        RecordingTask.objects.update_or_create(
            meeting_room=meeting_room,
            defaults={
                'status': 'recording',
                'start_time': timezone.now(),
                'record_id': f'record_{timezone.now().strftime("%Y%m%d%H%M%S")}'
            }
        )

        return Response(MeetingRoomSerializer(meeting_room).data)

    @action(detail=True, methods=['post'])
    def end_meeting(self, request, pk=None):
        """结束会议"""
        meeting_room = self.get_object()
        meeting_room.status = 'ended'
        meeting_room.end_time = timezone.now()
        meeting_room.save()

        # 更新录制任务
        recording_task = meeting_room.recording_tasks.order_by('-created_at').first()
        if recording_task:
            recording_task.status = 'ready'
            recording_task.end_time = timezone.now()
            if recording_task.start_time:
                recording_task.duration = int((recording_task.end_time - recording_task.start_time).total_seconds())
            recording_task.file_url = recording_task.file_url or f'https://meeting.tencent.com/mock-record/{recording_task.record_id or meeting_room.meeting_id}.mp4'
            recording_task.file_size = recording_task.file_size or 50 * 1024 * 1024
            recording_task.save()

            PlaybackFile.objects.update_or_create(
                recording_task=recording_task,
                defaults={
                    'file_url': recording_task.file_url,
                    'file_size': recording_task.file_size,
                    'duration': recording_task.duration,
                    'status': 'ready',
                    'view_permission': 'all'
                }
            )

        # 扣减课时
        self.deduct_hours(meeting_room.schedule)

        return Response(MeetingRoomSerializer(meeting_room).data)

    def deduct_hours(self, schedule):
        """扣减课时"""
        class_students = schedule.edu_class.class_students.filter(status='studying')
        for cs in class_students:
            try:
                account = StudentHoursAccount.objects.get(
                    student=cs.student,
                    course=schedule.course,
                    status='active'
                )
                if HoursFlow.objects.filter(account=account, schedule=schedule, type='deduct').exists():
                    continue
                before = account.remaining_hours
                account.used_hours += Decimal('1.0')
                account.save()

                HoursFlow.objects.create(
                    account=account,
                    schedule=schedule,
                    type='deduct',
                    hours=Decimal('1.0'),
                    balance_before=before,
                    balance_after=account.remaining_hours,
                    note=f'上课扣课 - {schedule.date}',
                    operator=None,
                )
            except StudentHoursAccount.DoesNotExist:
                pass


class MeetingRecordViewSet(viewsets.ModelViewSet):
    """参会记录视图"""
    queryset = MeetingRecord.objects.all()
    serializer_class = MeetingRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['meeting_room', 'role']

    @action(detail=False, methods=['get'])
    def by_schedule(self, request):
        """按课次查询"""
        schedule_id = request.query_params.get('schedule_id')
        meeting_room = MeetingRoom.objects.get(schedule_id=schedule_id)
        records = meeting_room.records.all()
        serializer = self.get_serializer(records, many=True)
        return Response(serializer.data)


class RecordingTaskViewSet(viewsets.ModelViewSet):
    """录制任务视图"""
    queryset = RecordingTask.objects.all()
    serializer_class = RecordingTaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['meeting_room', 'status']


class PlaybackFileViewSet(viewsets.ModelViewSet):
    """回放文件视图"""
    queryset = PlaybackFile.objects.all()
    serializer_class = PlaybackFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['recording_task', 'status']

    @action(detail=True, methods=['get'])
    def url(self, request, pk=None):
        """获取回放地址"""
        playback = self.get_object()
        if playback.status != 'ready':
            return Response({'error': '回放文件不可用'}, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        if playback.view_permission == 'none':
            return Response({'error': '无权限查看'}, status=status.HTTP_403_FORBIDDEN)

        return Response({'url': playback.file_url})


class ClassNoteViewSet(viewsets.ModelViewSet):
    """课堂备注视图"""
    queryset = ClassNote.objects.all()
    serializer_class = ClassNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['schedule']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
