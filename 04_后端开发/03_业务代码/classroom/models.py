from django.db import models
from django.conf import settings
from edu.models import Schedule


class MeetingRoom(models.Model):
    """会议室模型"""
    schedule = models.OneToOneField(Schedule, on_delete=models.CASCADE, verbose_name='课次', related_name='meeting_room')
    meeting_id = models.CharField(max_length=50, verbose_name='腾讯会议ID', blank=True)
    meeting_password = models.CharField(max_length=20, verbose_name='会议密码', blank=True)
    join_url = models.CharField(max_length=500, verbose_name='入会链接', blank=True)
    host_key = models.CharField(max_length=20, verbose_name='主持人密钥', blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[('pending', '未开始'), ('ongoing', '进行中'), ('ended', '已结束')], verbose_name='状态')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_meeting_room'
        verbose_name = '会议室'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['schedule'], name='idx_meeting_room_schedule'),
            models.Index(fields=['status'], name='idx_meeting_room_status'),
            models.Index(fields=['start_time'], name='idx_meeting_room_start_time'),
            models.Index(fields=['end_time'], name='idx_meeting_room_end_time'),
        ]

    def __str__(self):
        return f"{self.schedule} - {self.status}"


class MeetingRecord(models.Model):
    """参会记录模型"""
    meeting_room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, verbose_name='会议室', related_name='records')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='用户', related_name='meeting_records')
    username = models.CharField(max_length=50, verbose_name='参会用户名')
    role = models.CharField(max_length=20, choices=[('host', '主持人'), ('participant', '参会者')], verbose_name='角色')
    join_time = models.DateTimeField(verbose_name='入会时间')
    leave_time = models.DateTimeField(null=True, blank=True, verbose_name='离会时间')
    duration = models.IntegerField(default=0, verbose_name='参会时长(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_meeting_record'
        verbose_name = '参会记录'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['meeting_room'], name='idx_meeting_record_room'),
            models.Index(fields=['user'], name='idx_meeting_record_user'),
            models.Index(fields=['join_time'], name='idx_meeting_record_join_time'),
            models.Index(fields=['leave_time'], name='idx_meeting_record_leave_time'),
        ]

    def __str__(self):
        return f"{self.username} - {self.meeting_room}"


class RecordingTask(models.Model):
    """录制任务模型"""
    meeting_room = models.ForeignKey(MeetingRoom, on_delete=models.CASCADE, verbose_name='会议室', related_name='recording_tasks')
    record_id = models.CharField(max_length=50, verbose_name='录制ID', blank=True)
    status = models.CharField(max_length=20, default='pending', choices=[('pending', '待开始'), ('recording', '录制中'), ('transcoding', '转码中'), ('ready', '已完成'), ('failed', '失败')], verbose_name='状态')
    start_time = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    file_url = models.CharField(max_length=500, verbose_name='文件URL', blank=True)
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小')
    duration = models.IntegerField(default=0, verbose_name='时长(秒)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_recording_task'
        verbose_name = '录制任务'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['meeting_room'], name='idx_recording_task_room'),
            models.Index(fields=['status'], name='idx_recording_task_status'),
            models.Index(fields=['start_time'], name='idx_recording_task_start_time'),
            models.Index(fields=['end_time'], name='idx_recording_task_end_time'),
        ]

    def __str__(self):
        return f"{self.meeting_room} - {self.status}"


class PlaybackFile(models.Model):
    """回放文件模型"""
    recording_task = models.ForeignKey(RecordingTask, on_delete=models.CASCADE, verbose_name='录制任务', related_name='playback_files')
    file_url = models.CharField(max_length=500, verbose_name='回放地址')
    file_size = models.BigIntegerField(default=0, verbose_name='文件大小')
    duration = models.IntegerField(default=0, verbose_name='时长(秒)')
    status = models.CharField(max_length=20, default='pending', choices=[('pending', '待处理'), ('ready', '可用'), ('failed', '失败')], verbose_name='状态')
    view_permission = models.CharField(max_length=20, default='teacher', choices=[('all', '所有人'), ('teacher', '教师'), ('student', '学生'), ('none', '不可查看')], verbose_name='查看权限')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_playback_file'
        verbose_name = '回放文件'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['recording_task'], name='idx_playback_file_task'),
            models.Index(fields=['status'], name='idx_playback_file_status'),
            models.Index(fields=['view_permission'], name='idx_playback_file_permission'),
        ]

    def __str__(self):
        return f"{self.recording_task} - {self.status}"


class ClassNote(models.Model):
    """课堂备注模型"""
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='课次', related_name='class_notes')
    content = models.TextField(verbose_name='备注内容')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='创建人', related_name='class_notes')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_class_note'
        verbose_name = '课堂备注'
        verbose_name_plural = verbose_name
        indexes = [
            models.Index(fields=['schedule'], name='idx_class_note_schedule'),
            models.Index(fields=['created_by'], name='idx_class_note_creator'),
            models.Index(fields=['created_at'], name='idx_class_note_created_at'),
        ]

    def __str__(self):
        return f"{self.schedule} - {self.content[:20]}"