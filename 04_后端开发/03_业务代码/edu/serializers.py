from rest_framework import serializers
from .models import Subject, Course, Chapter, Section, CoursePackage, Student, Teacher, EduClass, ClassStudent, Schedule, RescheduleRecord, LeaveRecord, StudentHoursAccount, HoursFlow


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = '__all__'


class CourseListSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    chapter_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'subject', 'subject_name', 'cover', 'total_hours', 'duration', 'price', 'status', 'chapter_count', 'created_at']

    def get_chapter_count(self, obj):
        return obj.chapters.count()


class CourseDetailSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = '__all__'


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['name', 'code', 'subject', 'description', 'cover', 'total_hours', 'duration', 'price', 'status']


class CoursePackageSerializer(serializers.ModelSerializer):
    courses = CourseListSerializer(many=True, read_only=True)
    course_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = CoursePackage
        fields = '__all__'

    def create(self, validated_data):
        course_ids = validated_data.pop('course_ids', [])
        package = CoursePackage.objects.create(**validated_data)
        if course_ids:
            courses = Course.objects.filter(id__in=course_ids)
            package.courses.set(courses)
        return package


class StudentSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = '__all__'

    def get_class_name(self, obj):
        class_student = obj.class_students.filter(status='studying').first()
        return class_student.edu_class.name if class_student else None


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['name', 'phone', 'avatar', 'gender', 'birthday', 'grade', 'school', 'parent_name', 'parent_phone', 'status', 'enrollment_date']


class TeacherSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)
    subject_ids = serializers.ListField(write_only=True, required=False)
    class_count = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = '__all__'

    def get_class_count(self, obj):
        return obj.classes.filter(status='open').count()

    def create(self, validated_data):
        subject_ids = validated_data.pop('subject_ids', [])
        teacher = Teacher.objects.create(**validated_data)
        if subject_ids:
            subjects = Subject.objects.filter(id__in=subject_ids)
            teacher.subjects.set(subjects)
        return teacher


class ClassStudentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ClassStudent
        fields = ['id', 'student', 'student_id', 'join_date', 'status', 'created_at']


class EduClassListSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = EduClass
        fields = ['id', 'name', 'code', 'course', 'course_name', 'teacher', 'teacher_name', 'max_students', 'student_count', 'status', 'start_date', 'end_date']

    def get_student_count(self, obj):
        return obj.class_students.filter(status='studying').count()


class EduClassDetailSerializer(serializers.ModelSerializer):
    course = CourseListSerializer(read_only=True)
    teacher = TeacherSerializer(read_only=True)
    code = serializers.CharField(required=False, allow_blank=True)
    course_id = serializers.PrimaryKeyRelatedField(
        source='course', queryset=Course.objects.all(), write_only=True
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        source='teacher', queryset=Teacher.objects.all(), write_only=True
    )
    class_students = ClassStudentSerializer(many=True, read_only=True)

    class Meta:
        model = EduClass
        fields = [
            'id', 'name', 'code',
            'course', 'course_id',
            'teacher', 'teacher_id',
            'max_students', 'status',
            'start_date', 'end_date',
            'created_at', 'updated_at',
            'class_students',
        ]

    def to_internal_value(self, data):
        mutable = data.copy()
        if 'course' in mutable and 'course_id' not in mutable:
            mutable['course_id'] = mutable.get('course')
        if 'teacher' in mutable and 'teacher_id' not in mutable:
            mutable['teacher_id'] = mutable.get('teacher')
        return super().to_internal_value(mutable)

    def validate(self, attrs):
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')

        if self.instance:
            start_date = start_date or self.instance.start_date
            end_date = end_date if 'end_date' in attrs else self.instance.end_date

        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({'end_date': '结课日期不能早于开班日期'})

        return attrs


class ScheduleSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='edu_class.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = Schedule
        fields = '__all__'

    def create(self, validated_data):
        schedule = Schedule.objects.create(**validated_data)
        return schedule


class RescheduleRecordSerializer(serializers.ModelSerializer):
    original_schedule = ScheduleSerializer(read_only=True)
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    original_schedule_id = serializers.PrimaryKeyRelatedField(
        source='original_schedule', queryset=Schedule.objects.all(), write_only=True
    )
    new_schedule_id = serializers.PrimaryKeyRelatedField(
        source='new_schedule', queryset=Schedule.objects.all(), write_only=True, required=False, allow_null=True
    )

    class Meta:
        model = RescheduleRecord
        fields = [
            'id', 'original_schedule', 'original_schedule_id',
            'new_schedule', 'new_schedule_id',
            'type', 'reason', 'status',
            'applicant', 'applicant_name', 'approver', 'created_at'
        ]

    def to_internal_value(self, data):
        mutable = data.copy()
        if 'original_schedule' in mutable and 'original_schedule_id' not in mutable:
            mutable['original_schedule_id'] = mutable.get('original_schedule')
        if 'new_schedule' in mutable and 'new_schedule_id' not in mutable:
            mutable['new_schedule_id'] = mutable.get('new_schedule')
        return super().to_internal_value(mutable)

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('applicant', request.user)
        validated_data.setdefault('status', 'pending')
        return super().create(validated_data)


class LeaveRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)

    class Meta:
        model = LeaveRecord
        fields = '__all__'


class StudentHoursAccountSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)

    class Meta:
        model = StudentHoursAccount
        fields = ['id', 'student', 'student_name', 'course', 'course_name', 'total_hours', 'used_hours', 'frozen_hours', 'gift_hours', 'remaining_hours', 'status', 'expire_date']


class HoursFlowSerializer(serializers.ModelSerializer):
    operator_name = serializers.CharField(source='operator.username', read_only=True)

    class Meta:
        model = HoursFlow
        fields = '__all__'
