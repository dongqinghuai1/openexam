from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


class Subject(models.Model):
    """科目模型"""
    name = models.CharField(max_length=50, verbose_name='科目名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='科目编码')
    sort = models.IntegerField(default=0, verbose_name='排序')
    status = models.BooleanField(default=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_subject'
        verbose_name = '科目'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'id']

    def __str__(self):
        return self.name


class Course(models.Model):
    """课程模型"""
    name = models.CharField(max_length=100, verbose_name='课程名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='课程编码')
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, verbose_name='所属科目', related_name='courses')
    description = models.TextField(verbose_name='课程描述', blank=True)
    cover = models.CharField(max_length=500, verbose_name='封面图', blank=True)
    total_hours = models.IntegerField(verbose_name='总课时')
    duration = models.IntegerField(default=90, verbose_name='单次课时长(分钟)')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    status = models.CharField(max_length=20, default='active', choices=[('active', '在售'), ('archived', '已下架')], verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_course'
        verbose_name = '课程'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Chapter(models.Model):
    """章节模型"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, verbose_name='课程', related_name='chapters')
    name = models.CharField(max_length=100, verbose_name='章节名称')
    sort = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_chapter'
        verbose_name = '章节'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'id']

    def __str__(self):
        return self.name


class Section(models.Model):
    """小结模型"""
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, verbose_name='章节', related_name='sections')
    name = models.CharField(max_length=100, verbose_name='小结名称')
    content = models.TextField(verbose_name='内容', blank=True)
    sort = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_section'
        verbose_name = '小结'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'id']

    def __str__(self):
        return self.name


class CoursePackage(models.Model):
    """课程包模型"""
    name = models.CharField(max_length=100, verbose_name='套餐名称')
    courses = models.ManyToManyField(Course, verbose_name='包含课程', related_name='packages')
    hours = models.IntegerField(verbose_name='总课时')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    valid_days = models.IntegerField(default=365, verbose_name='有效期(天)')
    status = models.BooleanField(default=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_course_package'
        verbose_name = '课程包'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Student(models.Model):
    """学生模型"""
    name = models.CharField(max_length=50, verbose_name='姓名')
    phone = models.CharField(max_length=20, unique=True, verbose_name='手机号')
    avatar = models.CharField(max_length=500, verbose_name='头像URL', blank=True)
    gender = models.CharField(max_length=10, choices=[('male', '男'), ('female', '女')], verbose_name='性别', null=True, blank=True)
    birthday = models.DateField(verbose_name='出生日期', null=True, blank=True)
    grade = models.CharField(max_length=20, verbose_name='年级')
    school = models.CharField(max_length=100, verbose_name='学校', blank=True)
    parent_name = models.CharField(max_length=50, verbose_name='家长姓名')
    parent_phone = models.CharField(max_length=20, verbose_name='家长手机')
    status = models.CharField(max_length=20, default='active', choices=[('active', '在读'), ('inactive', '休学'), ('graduated', '毕业'), ('withdrawn', '退学')], verbose_name='状态')
    enrollment_date = models.DateField(verbose_name='入学日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_student'
        verbose_name = '学生'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Teacher(models.Model):
    """教师模型"""
    name = models.CharField(max_length=50, verbose_name='姓名')
    phone = models.CharField(max_length=20, unique=True, verbose_name='手机号')
    avatar = models.CharField(max_length=500, verbose_name='头像URL', blank=True)
    gender = models.CharField(max_length=10, choices=[('male', '男'), ('female', '女')], verbose_name='性别', null=True, blank=True)
    birthday = models.DateField(verbose_name='出生日期', null=True, blank=True)
    education = models.CharField(max_length=20, verbose_name='学历')
    major = models.CharField(max_length=50, verbose_name='专业')
    certification = models.CharField(max_length=50, verbose_name='证书', blank=True)
    subjects = models.ManyToManyField(Subject, verbose_name='擅长科目', related_name='teachers')
    status = models.CharField(max_length=20, default='active', choices=[('active', '在职'), ('resigned', '离职')], verbose_name='状态')
    hire_date = models.DateField(verbose_name='入职日期')
    salary_type = models.CharField(max_length=20, choices=[('hourly', '按课时'), ('fixed', '固定工资')], verbose_name='薪资类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_teacher'
        verbose_name = '教师'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class EduClass(models.Model):
    """班级模型"""
    name = models.CharField(max_length=100, verbose_name='班级名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='班级编码')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name='课程', related_name='classes')
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, verbose_name='授课教师', related_name='classes')
    max_students = models.IntegerField(default=20, verbose_name='最大人数')
    status = models.CharField(max_length=20, default='open', choices=[('open', '开班'), ('closed', '结课')], verbose_name='状态')
    start_date = models.DateField(verbose_name='开班日期')
    end_date = models.DateField(null=True, blank=True, verbose_name='结课日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_class'
        verbose_name = '班级'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.code:
            base = timezone.now().strftime('CLS%y%m%d%H%M%S')
            candidate = base
            index = 1
            while EduClass.objects.filter(code=candidate).exclude(pk=self.pk).exists():
                candidate = f'{base}{index:02d}'
                index += 1
            self.code = candidate
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({'end_date': '结课日期不能早于开班日期'})
        super().save(*args, **kwargs)


class ClassStudent(models.Model):
    """班级学生关联"""
    edu_class = models.ForeignKey(EduClass, on_delete=models.CASCADE, verbose_name='班级', related_name='class_students')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', related_name='class_students')
    join_date = models.DateField(verbose_name='入班日期')
    status = models.CharField(max_length=20, default='studying', choices=[('studying', '在读'), ('graduated', '已结课'), ('removed', '已移除')], verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_class_student'
        verbose_name = '班级学生'
        verbose_name_plural = verbose_name
        unique_together = ['edu_class', 'student']


class Schedule(models.Model):
    """排课模型"""
    edu_class = models.ForeignKey(EduClass, on_delete=models.CASCADE, verbose_name='班级', related_name='schedules')
    teacher = models.ForeignKey(Teacher, on_delete=models.PROTECT, verbose_name='教师', related_name='schedules')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name='课程', related_name='schedules')
    date = models.DateField(verbose_name='上课日期')
    start_time = models.TimeField(verbose_name='开始时间')
    end_time = models.TimeField(verbose_name='结束时间')
    room = models.CharField(max_length=50, verbose_name='教室', blank=True)
    status = models.CharField(max_length=20, default='scheduled', choices=[('scheduled', '已排课'), ('cancelled', '已取消'), ('completed', '已完成')], verbose_name='状态')
    note = models.TextField(verbose_name='备注', blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='创建人', related_name='created_schedules')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_schedule'
        verbose_name = '排课'
        verbose_name_plural = verbose_name
        ordering = ['date', 'start_time']
        unique_together = ['edu_class', 'date', 'start_time']


class RescheduleRecord(models.Model):
    """调课记录"""
    original_schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='原课次', related_name='original_records')
    new_schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='新课次', related_name='new_records', null=True, blank=True)
    type = models.CharField(max_length=20, choices=[('adjust', '调课'), ('reschedule', '补课'), ('supplement', '代课')], verbose_name='类型')
    reason = models.TextField(verbose_name='原因')
    status = models.CharField(max_length=20, default='pending', choices=[('pending', '待审批'), ('approved', '已批准'), ('rejected', '已拒绝')], verbose_name='状态')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='申请人', related_name='applicant_records')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='审批人', related_name='approved_records')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_reschedule_record'
        verbose_name = '调课记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class LeaveRecord(models.Model):
    """请假记录"""
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE, verbose_name='课次', related_name='leave_records')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', related_name='leave_records', null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='教师', related_name='leave_records', null=True, blank=True)
    type = models.CharField(max_length=20, choices=[('student', '学生请假'), ('teacher', '教师请假')], verbose_name='类型')
    reason = models.TextField(verbose_name='原因')
    status = models.CharField(max_length=20, default='pending', choices=[('pending', '待审批'), ('approved', '已批准'), ('rejected', '已拒绝')], verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_leave_record'
        verbose_name = '请假记录'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class StudentHoursAccount(models.Model):
    """学生课时账户"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', related_name='hours_accounts')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name='课程', related_name='hours_accounts')
    total_hours = models.DecimalField(max_digits=10, decimal_places=1, verbose_name='总课时')
    used_hours = models.DecimalField(max_digits=10, decimal_places=1, default=0, verbose_name='已用课时')
    frozen_hours = models.DecimalField(max_digits=10, decimal_places=1, default=0, verbose_name='冻结课时')
    gift_hours = models.DecimalField(max_digits=10, decimal_places=1, default=0, verbose_name='赠送课时')
    status = models.CharField(max_length=20, default='active', choices=[('active', '正常'), ('frozen', '冻结'), ('expired', '过期')], verbose_name='状态')
    expire_date = models.DateField(verbose_name='过期日期')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_student_hours_account'
        verbose_name = '学生课时账户'
        verbose_name_plural = verbose_name
        unique_together = ['student', 'course']

    @property
    def remaining_hours(self):
        return self.total_hours - self.used_hours - self.frozen_hours


class HoursFlow(models.Model):
    """课时流水"""
    account = models.ForeignKey(StudentHoursAccount, on_delete=models.CASCADE, verbose_name='账户', related_name='flows')
    schedule = models.ForeignKey(Schedule, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='课次', related_name='hours_flows')
    type = models.CharField(max_length=20, choices=[('deduct', '扣课'), ('gift', '赠送'), ('freeze', '冻结'), ('refund', '退款'), ('unfreeze', '解冻')], verbose_name='类型')
    hours = models.DecimalField(max_digits=10, decimal_places=1, verbose_name='课时数量')
    balance_before = models.DecimalField(max_digits=10, decimal_places=1, verbose_name='变动前余额')
    balance_after = models.DecimalField(max_digits=10, decimal_places=1, verbose_name='变动后余额')
    note = models.CharField(max_length=200, verbose_name='备注', blank=True)
    operator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='操作人', related_name='hours_flows')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_hours_flow'
        verbose_name = '课时流水'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
