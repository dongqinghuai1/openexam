from django.db import models
from django.conf import settings
from edu.models import Subject, Course, EduClass


class Question(models.Model):
    """题目模型"""
    TYPE_CHOICES = [
        ('single', '单选题'),
        ('multiple', '多选题'),
        ('blank', '填空题'),
        ('essay', '问答题'),
    ]
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='科目', related_name='questions')
    chapter = models.CharField(max_length=100, verbose_name='章节', blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name='题型')
    content = models.TextField(verbose_name='题目内容')
    options = models.JSONField(verbose_name='选项', blank=True, default=dict)
    answer = models.TextField(verbose_name='答案')
    analysis = models.TextField(verbose_name='解析', blank=True)
    difficulty = models.CharField(max_length=10, choices=[('easy', '简单'), ('medium', '中等'), ('hard', '困难')], verbose_name='难度')
    score = models.IntegerField(default=5, verbose_name='分值')
    status = models.BooleanField(default=True, verbose_name='状态')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_question'
        verbose_name = '题目'
        verbose_name_plural = verbose_name


class Paper(models.Model):
    """试卷模型"""
    name = models.CharField(max_length=100, verbose_name='试卷名称')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, verbose_name='科目')
    questions = models.ManyToManyField(Question, verbose_name='题目', through='PaperQuestion')
    total_score = models.IntegerField(default=0, verbose_name='总分')
    duration = models.IntegerField(default=90, verbose_name='时长(分钟)')
    status = models.CharField(max_length=20, default='draft', choices=[('draft', '草稿'), ('published', '已发布')], verbose_name='状态')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_paper'
        verbose_name = '试卷'
        verbose_name_plural = verbose_name


class PaperQuestion(models.Model):
    """试卷题目关联"""
    paper = models.ForeignKey(Paper, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    sort = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'tb_paper_question'
        unique_together = ['paper', 'question']


class Exam(models.Model):
    """考试模型"""
    name = models.CharField(max_length=100, verbose_name='考试名称')
    paper = models.ForeignKey(Paper, on_delete=models.PROTECT, verbose_name='试卷')
    edu_class = models.ForeignKey(EduClass, on_delete=models.CASCADE, verbose_name='班级', null=True, blank=True, related_name='exams')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(verbose_name='结束时间')
    status = models.CharField(max_length=20, default='pending', choices=[('pending', '待开始'), ('ongoing', '进行中'), ('ended', '已结束')], verbose_name='状态')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_exam'
        verbose_name = '考试'
        verbose_name_plural = verbose_name


class ExamAnswer(models.Model):
    """考试答案"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='考试', related_name='answers')
    student_id = models.IntegerField(verbose_name='学生ID')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='题目')
    answer = models.TextField(verbose_name='答案')
    score = models.IntegerField(null=True, blank=True, verbose_name='得分')
    is_auto = models.BooleanField(default=False, verbose_name='是否自动批改')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_exam_answer'
        unique_together = ['exam', 'student_id', 'question']


class ScoreRecord(models.Model):
    """成绩记录"""
    student_id = models.IntegerField(verbose_name='学生ID')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, verbose_name='考试', related_name='scores')
    total_score = models.IntegerField(verbose_name='总分')
    score = models.IntegerField(verbose_name='得分')
    rank = models.IntegerField(null=True, blank=True, verbose_name='排名')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_score_record'
        unique_together = ['student_id', 'exam']