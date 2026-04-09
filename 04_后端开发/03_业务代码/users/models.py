from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """用户模型"""
    phone = models.CharField(max_length=20, unique=True, verbose_name='手机号', null=True, blank=True)
    avatar = models.CharField(max_length=500, verbose_name='头像URL', blank=True)
    gender = models.CharField(max_length=10, choices=[('male', '男'), ('female', '女')], verbose_name='性别', null=True, blank=True)
    birthday = models.DateField(verbose_name='生日', null=True, blank=True)
    status = models.CharField(max_length=20, default='active', choices=[('active', '启用'), ('inactive', '禁用')], verbose_name='状态')
    roles = models.ManyToManyField('Role', verbose_name='角色', related_name='users', through='UserRole')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.username


class Role(models.Model):
    """角色模型"""
    name = models.CharField(max_length=50, verbose_name='角色名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='角色编码')
    description = models.TextField(verbose_name='描述', blank=True)
    permissions = models.ManyToManyField('Permission', verbose_name='权限', blank=True)
    status = models.BooleanField(default=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_role'
        verbose_name = '角色'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Permission(models.Model):
    """权限模型"""
    name = models.CharField(max_length=50, verbose_name='权限名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='权限编码')
    menu = models.ForeignKey('Menu', on_delete=models.SET_NULL, verbose_name='菜单', null=True, blank=True, related_name='permissions')
    api_path = models.CharField(max_length=100, verbose_name='API路径', blank=True)
    method = models.CharField(max_length=10, choices=[('GET', 'GET'), ('POST', 'POST'), ('PUT', 'PUT'), ('DELETE', 'DELETE')], verbose_name='请求方法', blank=True)
    description = models.CharField(max_length=200, verbose_name='描述', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_permission'
        verbose_name = '权限'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Menu(models.Model):
    """菜单模型"""
    name = models.CharField(max_length=50, verbose_name='菜单名称')
    path = models.CharField(max_length=100, verbose_name='路由路径', blank=True)
    component = models.CharField(max_length=100, verbose_name='组件路径', blank=True)
    icon = models.CharField(max_length=50, verbose_name='图标', blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, verbose_name='父菜单', null=True, blank=True, related_name='children')
    sort = models.IntegerField(default=0, verbose_name='排序')
    visible = models.BooleanField(default=True, verbose_name='是否可见')
    permission = models.CharField(max_length=100, verbose_name='权限标识', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_menu'
        verbose_name = '菜单'
        verbose_name_plural = verbose_name
        ordering = ['sort', 'id']
        constraints = [
            models.UniqueConstraint(fields=['name', 'parent'], name='unique_name_per_parent')
        ]

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """用户角色关联"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='role_users')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_user_role'
        verbose_name = '用户角色'
        verbose_name_plural = verbose_name
        unique_together = ['user', 'role']


class OperationLog(models.Model):
    """操作日志"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='操作人')
    username = models.CharField(max_length=50, verbose_name='操作人用户名')
    method = models.CharField(max_length=10, verbose_name='请求方法')
    path = models.CharField(max_length=200, verbose_name='请求路径')
    body = models.TextField(verbose_name='请求体', blank=True)
    response = models.TextField(verbose_name='响应内容', blank=True)
    ip = models.GenericIPAddressField(verbose_name='IP地址', null=True)
    duration = models.IntegerField(verbose_name='耗时(ms)', default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')

    class Meta:
        db_table = 'tb_operation_log'
        verbose_name = '操作日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class Notification(models.Model):
    """通知消息"""
    title = models.CharField(max_length=100, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    level = models.CharField(max_length=20, choices=[('info', '普通'), ('warning', '提醒'), ('urgent', '紧急')], default='info', verbose_name='级别')
    target_type = models.CharField(max_length=20, choices=[('all', '全体'), ('teacher', '教师'), ('student', '学生'), ('parent', '家长'), ('admin', '管理员')], default='all', verbose_name='发送对象')
    status = models.CharField(max_length=20, choices=[('draft', '草稿'), ('published', '已发布')], default='draft', verbose_name='状态')
    published_at = models.DateTimeField(null=True, blank=True, verbose_name='发布时间')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_notifications', verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_notification'
        verbose_name = '通知消息'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.title
