from rest_framework import serializers
from .models import MeetingRoom, MeetingRecord, RecordingTask, PlaybackFile, ClassNote


class MeetingRoomSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='schedule.edu_class.name', read_only=True)
    course_name = serializers.CharField(source='schedule.course.name', read_only=True)
    teacher_name = serializers.CharField(source='schedule.teacher.name', read_only=True)
    date = serializers.DateField(source='schedule.date', read_only=True)
    start_time = serializers.TimeField(source='schedule.start_time', read_only=True)
    end_time = serializers.TimeField(source='schedule.end_time', read_only=True)

    class Meta:
        model = MeetingRoom
        fields = '__all__'


class MeetingRecordSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = MeetingRecord
        fields = '__all__'


class RecordingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordingTask
        fields = '__all__'


class PlaybackFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlaybackFile
        fields = '__all__'


class ClassNoteSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = ClassNote
        fields = '__all__'