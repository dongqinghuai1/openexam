from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
from edu.models import Schedule, StudentHoursAccount, HoursFlow, Teacher, Student
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
    queryset = MeetingRoom.objects.select_related(
        'schedule',
        'schedule__teacher',
        'schedule__edu_class',
        'schedule__course',
    ).all()
    serializer_class = MeetingRoomSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']
    
    @action(detail=True, methods=['post'])
    def webrtc_signal(self, request, pk=None):
        """WebRTC信令交换"""
        meeting_room = self.get_object()
        if not self._can_access_meeting(request.user, meeting_room):
            return Response({'error': '无权限访问该会议室'}, status=status.HTTP_403_FORBIDDEN)
        
        signal = request.data.get('signal')
        if not signal:
            return Response({'error': '信令不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 使用Redis存储信令
        from django.core.cache import cache
        room_id = f"webrtc:room:{meeting_room.id}:signals"
        
        # 添加信令到队列
        signal_data = {
            'signal': signal,
            'sender': request.user.id,
            'timestamp': timezone.now().isoformat()
        }
        
        # 使用Redis列表存储信令
        import json
        cache.rpush(room_id, json.dumps(signal_data))
        
        # 限制队列大小
        cache.ltrim(room_id, -50, -1)
        
        return Response({'status': 'ok'})
    
    @action(detail=True, methods=['get'])
    def webrtc_signals(self, request, pk=None):
        """获取WebRTC信令"""
        meeting_room = self.get_object()
        if not self._can_access_meeting(request.user, meeting_room):
            return Response({'error': '无权限访问该会议室'}, status=status.HTTP_403_FORBIDDEN)
        
        # 使用Redis获取信令
        from django.core.cache import cache
        room_id = f"webrtc:room:{meeting_room.id}:signals"
        
        # 获取所有信令
        signals_data = cache.lrange(room_id, 0, -1)
        signals = []
        import json
        for data in signals_data:
            try:
                # 确保data是字符串类型
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                signals.append(json.loads(data))
            except Exception as e:
                print(f"解析信令失败: {e}")
                pass
        
        # 清除已读取的信令
        if len(signals) > 0:
            cache.delete(room_id)
        
        return Response({'signals': signals})

    def _get_user_phone(self, user):
        return getattr(user, 'phone', None) or getattr(user, 'username', None)

    def _get_role_codes(self, user):
        return set(user.roles.values_list('code', flat=True))

    def _get_role_names(self, user):
        return set(user.roles.values_list('name', flat=True))

    def _is_admin(self, user):
        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)
        return user.is_superuser or 'admin' in role_codes or '管理员' in role_names

    def _is_teacher_of_schedule(self, user, schedule):
        return Teacher.objects.filter(id=schedule.teacher_id, phone=self._get_user_phone(user)).exists()

    def _is_student_in_schedule(self, user, schedule):
        return schedule.edu_class.class_students.filter(student__phone=self._get_user_phone(user), status='studying').exists()

    def _is_parent_of_schedule(self, user, schedule):
        return schedule.edu_class.class_students.filter(student__parent_phone=self._get_user_phone(user), status='studying').exists()

    def _can_access_meeting(self, user, meeting_room):
        if self._is_admin(user):
            return True

        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)
        schedule = meeting_room.schedule

        if 'teacher' in role_codes or '教师' in role_names:
            return self._is_teacher_of_schedule(user, schedule)
        if 'student' in role_codes or '学生' in role_names:
            return self._is_student_in_schedule(user, schedule)
        if 'parent' in role_codes or '家长' in role_names:
            return self._is_parent_of_schedule(user, schedule)
        return False

    def _can_manage_meeting(self, user, meeting_room):
        return self._is_admin(user) or self._is_teacher_of_schedule(user, meeting_room.schedule)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if self._is_admin(user):
            return queryset

        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)
        user_phone = self._get_user_phone(user)
        filters = Q(pk__in=[])

        if 'teacher' in role_codes or '教师' in role_names:
            filters |= Q(schedule__teacher__phone=user_phone)

        if 'student' in role_codes or '学生' in role_names:
            student_ids = Student.objects.filter(phone=user_phone).values_list('id', flat=True)
            filters |= Q(
                schedule__edu_class__class_students__student_id__in=student_ids,
                schedule__edu_class__class_students__status='studying',
            )

        if 'parent' in role_codes or '家长' in role_names:
            filters |= Q(
                schedule__edu_class__class_students__student__parent_phone=user_phone,
                schedule__edu_class__class_students__status='studying',
            )

        return queryset.filter(filters).distinct()

    @action(detail=False, methods=['post'])
    def create_meeting(self, request):
        """创建课堂"""
        schedule_id = request.data.get('schedule_id')
        try:
            schedule = Schedule.objects.get(id=schedule_id)
        except Schedule.DoesNotExist:
            return Response({'error': '课次不存在'}, status=status.HTTP_404_NOT_FOUND)

        if not (self._is_admin(request.user) or self._is_teacher_of_schedule(request.user, schedule)):
            return Response({'error': '无权限为该课次创建课堂'}, status=status.HTTP_403_FORBIDDEN)

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
        if not self._can_access_meeting(request.user, meeting_room):
            return Response({'error': '无权限获取入会信息'}, status=status.HTTP_403_FORBIDDEN)

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
        if not self._can_manage_meeting(request.user, meeting_room):
            return Response({'error': '无权限开始会议'}, status=status.HTTP_403_FORBIDDEN)

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
        if not self._can_manage_meeting(request.user, meeting_room):
            return Response({'error': '无权限结束会议'}, status=status.HTTP_403_FORBIDDEN)

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
    queryset = PlaybackFile.objects.select_related(
        'recording_task',
        'recording_task__meeting_room',
        'recording_task__meeting_room__schedule',
        'recording_task__meeting_room__schedule__teacher',
        'recording_task__meeting_room__schedule__edu_class',
    ).all()
    serializer_class = PlaybackFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['recording_task', 'status']

    def _get_user_phone(self, user):
        return getattr(user, 'phone', None) or getattr(user, 'username', None)

    def _get_role_codes(self, user):
        return set(user.roles.values_list('code', flat=True))

    def _get_role_names(self, user):
        return set(user.roles.values_list('name', flat=True))

    def _is_admin(self, user):
        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)
        return user.is_superuser or 'admin' in role_codes or '管理员' in role_names

    def _can_access_playback(self, playback, user):
        if playback.status != 'ready' or playback.view_permission == 'none':
            return False

        if self._is_admin(user):
            return True

        schedule = playback.recording_task.meeting_room.schedule
        user_phone = self._get_user_phone(user)
        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)

        is_teacher = 'teacher' in role_codes or '教师' in role_names
        is_student = 'student' in role_codes or '学生' in role_names
        is_parent = 'parent' in role_codes or '家长' in role_names

        if is_teacher and playback.view_permission in ['teacher', 'all']:
            return Teacher.objects.filter(id=schedule.teacher_id, phone=user_phone).exists()

        if is_student and playback.view_permission in ['student', 'all']:
            return schedule.edu_class.class_students.filter(student__phone=user_phone, status='studying').exists()

        if is_parent and playback.view_permission == 'all':
            return schedule.edu_class.class_students.filter(student__parent_phone=user_phone, status='studying').exists()

        return False

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user

        if self._is_admin(user):
            return queryset.exclude(view_permission='none')

        user_phone = self._get_user_phone(user)
        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)
        filters = Q(pk__in=[])

        if 'teacher' in role_codes or '教师' in role_names:
            filters |= Q(
                view_permission__in=['teacher', 'all'],
                recording_task__meeting_room__schedule__teacher__phone=user_phone,
            )

        if 'student' in role_codes or '学生' in role_names:
            student_ids = Student.objects.filter(phone=user_phone).values_list('id', flat=True)
            filters |= Q(
                view_permission__in=['student', 'all'],
                recording_task__meeting_room__schedule__edu_class__class_students__student_id__in=student_ids,
                recording_task__meeting_room__schedule__edu_class__class_students__status='studying',
            )

        if 'parent' in role_codes or '家长' in role_names:
            filters |= Q(
                view_permission='all',
                recording_task__meeting_room__schedule__edu_class__class_students__student__parent_phone=user_phone,
                recording_task__meeting_room__schedule__edu_class__class_students__status='studying',
            )

        return queryset.filter(filters).exclude(view_permission='none').distinct()

    @action(detail=True, methods=['get'])
    def url(self, request, pk=None):
        """获取回放地址"""
        playback = self.get_object()
        if playback.status != 'ready':
            return Response({'error': '回放文件不可用'}, status=status.HTTP_400_BAD_REQUEST)

        if not self._can_access_playback(playback, request.user):
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
