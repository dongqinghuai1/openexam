from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Q
from .models import Question, Paper, Exam, ExamAnswer, ScoreRecord
from .serializers import QuestionSerializer, PaperSerializer, ExamSerializer, ScoreRecordSerializer
from edu.models import Student, Teacher


class QuestionViewSet(viewsets.ModelViewSet):
    """题目管理视图"""
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['subject', 'type', 'difficulty', 'status']
    search_fields = ['content']


class PaperViewSet(viewsets.ModelViewSet):
    """试卷管理视图"""
    queryset = Paper.objects.all()
    serializer_class = PaperSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['subject', 'status']


class ExamViewSet(viewsets.ModelViewSet):
    """考试管理视图"""
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['edu_class', 'status']

    def get_permissions(self):
        if self.action == 'submit':
            return [permissions.AllowAny()]
        return super().get_permissions()

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

    def get_queryset(self):
        queryset = Exam.objects.select_related('paper', 'edu_class').all().order_by('-start_time')
        user = getattr(self.request, 'user', None)
        if not user or not user.is_authenticated or self._is_admin(user):
            return queryset

        user_phone = self._get_user_phone(user)
        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)
        filters = Q(pk__in=[])

        if 'teacher' in role_codes or '教师' in role_names:
            teacher_ids = Teacher.objects.filter(phone=user_phone).values_list('id', flat=True)
            filters |= Q(edu_class__teacher_id__in=teacher_ids)

        if 'student' in role_codes or '学生' in role_names:
            student_ids = Student.objects.filter(phone=user_phone).values_list('id', flat=True)
            filters |= Q(
                edu_class__class_students__student_id__in=student_ids,
                edu_class__class_students__status='studying',
            )

        if 'parent' in role_codes or '家长' in role_names:
            filters |= Q(
                edu_class__class_students__student__parent_phone=user_phone,
                edu_class__class_students__status='studying',
            )

        return queryset.filter(filters).distinct()

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布考试"""
        exam = self.get_object()
        exam.status = 'ongoing' if exam.start_time <= timezone.now() <= exam.end_time else 'pending'
        exam.save()
        return Response({'message': '考试已发布'})

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        """提交考试答案并生成成绩记录"""
        exam = self.get_object()
        answers = request.data.get('answers') or {}
        student_id = request.data.get('student_id')

        if not student_id:
            student = Student.objects.order_by('id').first()
            if not student:
                return Response({'error': '缺少 student_id，且系统中不存在学生数据'}, status=status.HTTP_400_BAD_REQUEST)
            student_id = student.id

        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': '学生不存在'}, status=status.HTTP_404_NOT_FOUND)

        if exam.edu_class and not exam.edu_class.class_students.filter(student=student, status='studying').exists():
            return Response({'error': '当前学生不在本场考试所属班级中'}, status=status.HTTP_403_FORBIDDEN)

        questions = list(exam.paper.questions.all().order_by('paperquestion__sort', 'id'))
        if not questions:
            return Response({'error': '当前考试未配置题目'}, status=status.HTTP_400_BAD_REQUEST)

        total_score = 0
        earned_score = 0

        for index, question in enumerate(questions):
            raw_answer = answers.get(str(index), answers.get(index, ''))
            submitted_answer = '' if raw_answer is None else str(raw_answer)
            total_score += question.score

            normalized_expected = str(question.answer).strip()
            normalized_submitted = submitted_answer.strip()
            is_auto = question.type in ['single', 'multiple', 'blank']
            score = question.score if is_auto and normalized_submitted == normalized_expected else 0
            earned_score += score

            ExamAnswer.objects.update_or_create(
                exam=exam,
                student_id=student_id,
                question=question,
                defaults={
                    'answer': submitted_answer,
                    'score': score,
                    'is_auto': is_auto,
                },
            )

        score_record, _ = ScoreRecord.objects.update_or_create(
            exam=exam,
            student_id=student_id,
            defaults={
                'total_score': total_score,
                'score': earned_score,
            },
        )

        ranked_scores = list(ScoreRecord.objects.filter(exam=exam).order_by('-score', 'created_at'))
        for rank, item in enumerate(ranked_scores, start=1):
            if item.rank != rank:
                item.rank = rank
                item.save(update_fields=['rank'])
        score_record.refresh_from_db()

        return Response({
            'message': '提交成功',
            'student_id': student_id,
            'score': score_record.score,
            'total_score': score_record.total_score,
            'rank': score_record.rank,
        })


class ScoreRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """成绩记录视图"""
    queryset = ScoreRecord.objects.all()
    serializer_class = ScoreRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['exam', 'student_id']

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

    def get_queryset(self):
        queryset = super().get_queryset().select_related('exam', 'exam__edu_class', 'exam__edu_class__teacher')
        user = self.request.user

        if self._is_admin(user):
            return queryset

        user_phone = self._get_user_phone(user)
        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)
        filters = Q(pk__in=[])

        if 'teacher' in role_codes or '教师' in role_names:
            teacher_ids = Teacher.objects.filter(phone=user_phone).values_list('id', flat=True)
            filters |= Q(exam__edu_class__teacher_id__in=teacher_ids)

        if 'student' in role_codes or '学生' in role_names:
            student_ids = list(Student.objects.filter(phone=user_phone).values_list('id', flat=True))
            filters |= Q(student_id__in=student_ids)

        if 'parent' in role_codes or '家长' in role_names:
            student_ids = list(Student.objects.filter(parent_phone=user_phone).values_list('id', flat=True))
            filters |= Q(student_id__in=student_ids)

        return queryset.filter(filters).distinct()

    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """按学生查询"""
        queryset = self.filter_queryset(self.get_queryset())
        student_id = request.query_params.get('student_id')
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
