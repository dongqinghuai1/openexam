from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Question, Paper, Exam, ExamAnswer, ScoreRecord
from .serializers import QuestionSerializer, PaperSerializer, ExamSerializer, ScoreRecordSerializer
from edu.models import Student


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

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布考试"""
        exam = self.get_object()
        exam.status = 'pending'
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

        return Response({
            'message': '提交成功',
            'student_id': student_id,
            'score': score_record.score,
            'total_score': score_record.total_score,
        })


class ScoreRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """成绩记录视图"""
    queryset = ScoreRecord.objects.all()
    serializer_class = ScoreRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['exam']

    @action(detail=False, methods=['get'])
    def by_student(self, request):
        """按学生查询"""
        student_id = request.query_params.get('student_id')
        scores = ScoreRecord.objects.filter(student_id=student_id)
        serializer = self.get_serializer(scores, many=True)
        return Response(serializer.data)
