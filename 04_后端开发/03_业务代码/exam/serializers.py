from rest_framework import serializers
from exam.models import Question, Paper, PaperQuestion, Exam, ExamAnswer, ScoreRecord
from finance.models import Order, PaymentRecord, RefundRecord


class QuestionSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'


class PaperSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Paper
        fields = '__all__'

    def get_question_count(self, obj):
        return obj.questions.count()


class ExamSerializer(serializers.ModelSerializer):
    paper_name = serializers.CharField(source='paper.name', read_only=True)
    class_name = serializers.CharField(source='edu_class.name', read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'


class ScoreRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreRecord
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'


class PaymentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentRecord
        fields = '__all__'


class RefundRecordSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    order_no = serializers.CharField(source='order.order_no', read_only=True)

    class Meta:
        model = RefundRecord
        fields = '__all__'