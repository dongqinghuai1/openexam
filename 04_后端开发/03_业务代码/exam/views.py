from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Question, Paper, Exam, ExamAnswer, ScoreRecord
from .serializers import QuestionSerializer, PaperSerializer, ExamSerializer, ScoreRecordSerializer
from edu.models import StudentHoursAccount


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