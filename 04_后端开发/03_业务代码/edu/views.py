from datetime import date
from django.core.exceptions import ValidationError as DjangoValidationError
from decimal import Decimal
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters import rest_framework as filters
from .models import Subject, Course, Chapter, Section, CoursePackage, Student, Teacher, EduClass, ClassStudent, Schedule, RescheduleRecord, LeaveRecord, StudentHoursAccount, HoursFlow
from . import serializers
from .serializers import (
    SubjectSerializer, ChapterSerializer, SectionSerializer,
    CourseListSerializer, CourseDetailSerializer, CourseCreateSerializer,
    CoursePackageSerializer, StudentSerializer, StudentCreateSerializer, TeacherSerializer,
    EduClassListSerializer, EduClassDetailSerializer, ClassStudentSerializer,
    ScheduleSerializer, RescheduleRecordSerializer, LeaveRecordSerializer,
    StudentHoursAccountSerializer, HoursFlowSerializer
)


class SubjectViewSet(viewsets.ModelViewSet):
    """科目管理视图"""
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status']


class CourseViewSet(viewsets.ModelViewSet):
    """课程管理视图"""
    queryset = Course.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['subject', 'status']
    search_fields = ['name', 'code']

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CourseCreateSerializer
        return CourseDetailSerializer


class ChapterViewSet(viewsets.ModelViewSet):
    """章节管理视图"""
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['course']


class StudentViewSet(viewsets.ModelViewSet):
    """学生管理视图"""
    queryset = Student.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'gender', 'grade']
    search_fields = ['name', 'phone', 'parent_phone']

    def get_serializer_class(self):
        if self.action == 'create':
            return StudentCreateSerializer
        return StudentSerializer

    @action(detail=True, methods=['get'])
    def hours_accounts(self, request, pk=None):
        """获取学生课时账户"""
        student = self.get_object()
        accounts = student.hours_accounts.all()
        serializer = StudentHoursAccountSerializer(accounts, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        """获取学生课表"""
        student = self.get_object()
        class_ids = student.class_students.filter(status='studying').values_list('edu_class_id', flat=True)
        schedules = Schedule.objects.filter(edu_class_id__in=class_ids).order_by('date', 'start_time')
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


class TeacherViewSet(viewsets.ModelViewSet):
    """教师管理视图"""
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'gender']
    search_fields = ['name', 'phone']

    @action(detail=True, methods=['get'])
    def schedules(self, request, pk=None):
        """获取教师课表"""
        teacher = self.get_object()
        schedules = teacher.schedules.filter(status='scheduled').order_by('date', 'start_time')
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)


class EduClassViewSet(viewsets.ModelViewSet):
    """班级管理视图"""
    queryset = EduClass.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['course', 'teacher', 'status']

    def get_serializer_class(self):
        if self.action == 'list':
            return EduClassListSerializer
        return EduClassDetailSerializer

    def perform_create(self, serializer):
        instance = EduClass(**serializer.validated_data)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict)
        instance.save()

    def perform_update(self, serializer):
        instance = serializer.instance
        for field, value in serializer.validated_data.items():
            setattr(instance, field, value)
        try:
            instance.full_clean()
        except DjangoValidationError as exc:
            raise ValidationError(exc.message_dict)
        instance.save()

    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """添加学生到班级"""
        edu_class = self.get_object()
        student_id = request.data.get('student_id')
        join_date = request.data.get('join_date', date.today())

        if edu_class.class_students.filter(status='studying').count() >= edu_class.max_students:
            return Response({'error': '班级人数已满'}, status=status.HTTP_400_BAD_REQUEST)

        student = Student.objects.get(id=student_id)
        class_student, created = ClassStudent.objects.update_or_create(
            edu_class=edu_class, student=student,
            defaults={'join_date': join_date, 'status': 'studying'}
        )
        return Response(ClassStudentSerializer(class_student).data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['delete'], url_path='remove_student/(?P<student_id>[^/.]+)')
    def remove_student(self, request, pk=None, student_id=None):
        """移除学生"""
        edu_class = self.get_object()
        try:
            class_student = edu_class.class_students.get(student_id=student_id)
            class_student.status = 'removed'
            class_student.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ClassStudent.DoesNotExist:
            return Response({'error': '学生不在该班级'}, status=status.HTTP_404_NOT_FOUND)


class ScheduleViewSet(viewsets.ModelViewSet):
    """排课管理视图"""
    queryset = Schedule.objects.all()
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['edu_class', 'teacher', 'course', 'date', 'status']

    def perform_create(self, serializer):
        schedule = serializer.save(created_by=self.request.user)
        # 检测冲突
        conflicts = self.check_conflicts(schedule)
        if conflicts:
            # 可以选择返回警告或阻止创建
            pass

    def check_conflicts(self, schedule):
        """检测排课冲突"""
        conflicts = []
        # 教师冲突
        teacher_conflicts = Schedule.objects.filter(
            teacher=schedule.teacher,
            date=schedule.date,
            status='scheduled'
        ).exclude(id=schedule.id).filter(
            start_time__lt=schedule.end_time,
            end_time__gt=schedule.start_time
        )
        if teacher_conflicts.exists():
            conflicts.append('教师时间冲突')

        # 班级冲突
        class_conflicts = Schedule.objects.filter(
            edu_class=schedule.edu_class,
            date=schedule.date,
            status='scheduled'
        ).exclude(id=schedule.id).filter(
            start_time__lt=schedule.end_time,
            end_time__gt=schedule.start_time
        )
        if class_conflicts.exists():
            conflicts.append('班级时间冲突')

        return conflicts

    @action(detail=False, methods=['get'])
    def calendar(self, request):
        """日历视图"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        queryset = self.get_queryset().filter(date__range=[start_date, end_date])
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """完成上课并扣减课时"""
        schedule = self.get_object()
        if schedule.status == 'completed':
            return Response({'error': '当前课次已完成'}, status=status.HTTP_400_BAD_REQUEST)

        class_students = schedule.edu_class.class_students.filter(status='studying')
        for cs in class_students:
            try:
                account = StudentHoursAccount.objects.get(
                    student=cs.student,
                    course=schedule.course,
                    status='active'
                )
            except StudentHoursAccount.DoesNotExist:
                continue

            already_deducted = HoursFlow.objects.filter(
                account=account,
                schedule=schedule,
                type='deduct'
            ).exists()
            if already_deducted:
                continue

            before = account.remaining_hours
            account.used_hours += Decimal('1.0')
            account.save(update_fields=['used_hours', 'updated_at'])

            HoursFlow.objects.create(
                account=account,
                schedule=schedule,
                type='deduct',
                hours=Decimal('1.0'),
                balance_before=before,
                balance_after=account.remaining_hours,
                note=f'上课扣课 - {schedule.date}',
                operator=request.user,
            )

        schedule.status = 'completed'
        schedule.save(update_fields=['status', 'updated_at'])
        return Response(self.get_serializer(schedule).data)


class RescheduleRecordViewSet(viewsets.ModelViewSet):
    """调课记录视图"""
    queryset = RescheduleRecord.objects.all()
    serializer_class = RescheduleRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'type']

    def get_queryset(self):
        return RescheduleRecord.objects.select_related(
            'original_schedule', 'new_schedule', 'applicant', 'approver'
        ).all()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        record = self.get_object()
        if record.status != 'pending':
            return Response({'error': '当前调课记录不可审批'}, status=status.HTTP_400_BAD_REQUEST)
        record.status = 'approved'
        record.approver = request.user
        record.save(update_fields=['status', 'approver'])
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        record = self.get_object()
        if record.status != 'pending':
            return Response({'error': '当前调课记录不可审批'}, status=status.HTTP_400_BAD_REQUEST)
        record.status = 'rejected'
        record.approver = request.user
        record.save(update_fields=['status', 'approver'])
        return Response(self.get_serializer(record).data)


class LeaveRecordViewSet(viewsets.ModelViewSet):
    """请假记录视图"""
    queryset = LeaveRecord.objects.all()
    serializer_class = LeaveRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['type', 'status', 'student', 'teacher']

    def get_queryset(self):
        return LeaveRecord.objects.select_related('schedule', 'student', 'teacher').all()

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        record = self.get_object()
        if record.status != 'pending':
            return Response({'error': '当前请假记录不可审批'}, status=status.HTTP_400_BAD_REQUEST)
        record.status = 'approved'
        record.save(update_fields=['status'])
        return Response(self.get_serializer(record).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        record = self.get_object()
        if record.status != 'pending':
            return Response({'error': '当前请假记录不可审批'}, status=status.HTTP_400_BAD_REQUEST)
        record.status = 'rejected'
        record.save(update_fields=['status'])
        return Response(self.get_serializer(record).data)


class StudentHoursAccountViewSet(viewsets.ModelViewSet):
    """学生课时账户视图"""
    queryset = StudentHoursAccount.objects.all()
    serializer_class = StudentHoursAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'course', 'status']

    def get_queryset(self):
        return StudentHoursAccount.objects.select_related('student', 'course').all()

    @action(detail=True, methods=['post'])
    def gift(self, request, pk=None):
        account = self.get_object()
        hours = request.data.get('hours')
        note = request.data.get('note', '赠送课时')

        try:
            hours = Decimal(str(hours))
        except Exception:
            return Response({'error': '课时数量格式不正确'}, status=status.HTTP_400_BAD_REQUEST)

        if hours <= 0:
            return Response({'error': '赠送课时必须大于 0'}, status=status.HTTP_400_BAD_REQUEST)

        before = account.remaining_hours
        account.gift_hours += hours
        account.save(update_fields=['gift_hours', 'updated_at'])

        HoursFlow.objects.create(
            account=account,
            type='gift',
            hours=hours,
            balance_before=before,
            balance_after=account.remaining_hours,
            note=note,
            operator=request.user,
        )
        return Response(StudentHoursAccountSerializer(account).data)

    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        account = self.get_object()
        hours = request.data.get('hours')
        note = request.data.get('note', '冻结课时')

        try:
            hours = Decimal(str(hours))
        except Exception:
            return Response({'error': '课时数量格式不正确'}, status=status.HTTP_400_BAD_REQUEST)

        if hours <= 0:
            return Response({'error': '冻结课时必须大于 0'}, status=status.HTTP_400_BAD_REQUEST)
        if account.remaining_hours < hours:
            return Response({'error': '剩余课时不足，无法冻结'}, status=status.HTTP_400_BAD_REQUEST)

        before = account.remaining_hours
        account.frozen_hours += hours
        if account.status == 'active':
            account.status = 'frozen'
        account.save(update_fields=['frozen_hours', 'status', 'updated_at'])

        HoursFlow.objects.create(
            account=account,
            type='freeze',
            hours=hours,
            balance_before=before,
            balance_after=account.remaining_hours,
            note=note,
            operator=request.user,
        )
        return Response(StudentHoursAccountSerializer(account).data)

    @action(detail=True, methods=['post'])
    def unfreeze(self, request, pk=None):
        account = self.get_object()
        hours = request.data.get('hours')
        note = request.data.get('note', '解冻课时')

        try:
            hours = Decimal(str(hours))
        except Exception:
            return Response({'error': '课时数量格式不正确'}, status=status.HTTP_400_BAD_REQUEST)

        if hours <= 0:
            return Response({'error': '解冻课时必须大于 0'}, status=status.HTTP_400_BAD_REQUEST)
        if account.frozen_hours < hours:
            return Response({'error': '冻结课时不足，无法解冻'}, status=status.HTTP_400_BAD_REQUEST)

        before = account.remaining_hours
        account.frozen_hours -= hours
        if account.frozen_hours == 0 and account.status == 'frozen':
            account.status = 'active'
        account.save(update_fields=['frozen_hours', 'status', 'updated_at'])

        HoursFlow.objects.create(
            account=account,
            type='unfreeze',
            hours=hours,
            balance_before=before,
            balance_after=account.remaining_hours,
            note=note,
            operator=request.user,
        )
        return Response(StudentHoursAccountSerializer(account).data)


class HoursFlowViewSet(viewsets.ReadOnlyModelViewSet):
    """课时流水视图"""
    queryset = HoursFlow.objects.all()
    serializer_class = HoursFlowSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['account', 'type']

    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """按学生查询"""
        student_id = request.query_params.get('student_id')
        accounts = StudentHoursAccount.objects.filter(student_id=student_id)
        account_ids = [a.id for a in accounts]
        flows = HoursFlow.objects.filter(account_id__in=account_ids)
        serializer = self.get_serializer(flows, many=True)
        return Response(serializer.data)
