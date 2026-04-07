from django.apps import AppConfig


class ExamConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'exam'
    verbose_name = '考试测评'


class FinanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'finance'
    verbose_name = '财务管理'