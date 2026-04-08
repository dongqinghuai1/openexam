from rest_framework import serializers
from exam.models import Question, Paper, PaperQuestion, Exam, ExamAnswer, ScoreRecord
from finance.models import Order, PaymentRecord, RefundRecord
from django.db import transaction


class QuestionSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Question
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('created_by', request.user)
        return super().create(validated_data)


class ExamQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'type', 'content', 'options', 'score']

    def get_options(self, obj):
        if not obj.options:
            return []
        return [{'key': key, 'value': value} for key, value in obj.options.items()]


class PaperSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    question_count = serializers.SerializerMethodField()
    question_ids = serializers.ListField(child=serializers.IntegerField(), write_only=True, required=False)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Paper
        fields = '__all__'

    def get_question_count(self, obj):
        return obj.questions.count()

    @transaction.atomic
    def create(self, validated_data):
        question_ids = validated_data.pop('question_ids', [])
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('created_by', request.user)
        paper = Paper.objects.create(**validated_data)
        total_score = 0
        for index, question_id in enumerate(question_ids, start=1):
            question = Question.objects.get(id=question_id)
            PaperQuestion.objects.create(paper=paper, question=question, sort=index)
            total_score += question.score
        if question_ids:
            paper.total_score = total_score
            paper.save(update_fields=['total_score'])
        return paper

    @transaction.atomic
    def update(self, instance, validated_data):
        question_ids = validated_data.pop('question_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if question_ids is not None:
            instance.paperquestion_set.all().delete()
            total_score = 0
            for index, question_id in enumerate(question_ids, start=1):
                question = Question.objects.get(id=question_id)
                PaperQuestion.objects.create(paper=instance, question=question, sort=index)
                total_score += question.score
            instance.total_score = total_score
            instance.save(update_fields=['total_score'])
        return instance

    def to_internal_value(self, data):
        mutable = data.copy()
        if 'questions' in mutable and 'question_ids' not in mutable:
            mutable['question_ids'] = mutable.get('questions')
        return super().to_internal_value(mutable)


class ExamSerializer(serializers.ModelSerializer):
    paper_name = serializers.CharField(source='paper.name', read_only=True)
    class_name = serializers.CharField(source='edu_class.name', read_only=True)
    subject_name = serializers.CharField(source='paper.subject.name', read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        fields = '__all__'

    def get_questions(self, obj):
        questions = obj.paper.questions.all().order_by('paperquestion__sort', 'id')
        return ExamQuestionSerializer(questions, many=True).data

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        if self.instance:
            start_time = start_time or self.instance.start_time
            end_time = end_time or self.instance.end_time
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({'end_time': '结束时间必须晚于开始时间'})
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('created_by', request.user)
        return super().create(validated_data)


class ScoreRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    exam_name = serializers.CharField(source='exam.name', read_only=True)

    class Meta:
        model = ScoreRecord
        fields = '__all__'

    def get_student_name(self, obj):
        from edu.models import Student
        try:
            return Student.objects.get(id=obj.student_id).name
        except:
            return None


class ExamAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAnswer
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
