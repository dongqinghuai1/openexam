"""
权限管理系统初始化脚本
用于初始化默认的权限数据和角色
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduadmin.settings')
django.setup()

from django.core.management.base import BaseCommand
from users.models import Permission, Role, User
from django.db import transaction


# 简化的权限列表
PERMISSIONS = [
    # ========== 系统管理 ==========
    {'name': '系统管理', 'code': 'system_management', 'api_path': '/api/users/', 'method': '*', 'description': '系统管理功能'},
    
    # ========== 教务管理 ==========
    {'name': '学生管理', 'code': 'student_management', 'api_path': '/api/edu/students/', 'method': '*', 'description': '学生管理功能'},
    {'name': '教师管理', 'code': 'teacher_management', 'api_path': '/api/edu/teachers/', 'method': '*', 'description': '教师管理功能'},
    {'name': '课程管理', 'code': 'course_management', 'api_path': '/api/edu/courses/', 'method': '*', 'description': '课程管理功能'},
    {'name': '班级管理', 'code': 'class_management', 'api_path': '/api/edu/classes/', 'method': '*', 'description': '班级管理功能'},
    {'name': '排课管理', 'code': 'schedule_management', 'api_path': '/api/edu/schedules/', 'method': '*', 'description': '排课管理功能'},
    {'name': '调课管理', 'code': 'reschedule_management', 'api_path': '/api/edu/reschedules/', 'method': '*', 'description': '调课记录'},
    {'name': '请假管理', 'code': 'leave_management', 'api_path': '/api/edu/leaves/', 'method': '*', 'description': '请假记录'},
    {'name': '课时管理', 'code': 'hours_management', 'api_path': '/api/edu/student-hours/', 'method': '*', 'description': '课时管理'},
    
    # ========== 考试管理 ==========
    {'name': '题库管理', 'code': 'question_management', 'api_path': '/api/exam/questions/', 'method': '*', 'description': '题库管理'},
    {'name': '试卷管理', 'code': 'paper_management', 'api_path': '/api/exam/papers/', 'method': '*', 'description': '试卷管理'},
    {'name': '考试管理', 'code': 'exam_management', 'api_path': '/api/exam/exams/', 'method': '*', 'description': '考试管理'},
    {'name': '成绩管理', 'code': 'score_management', 'api_path': '/api/exam/scores/', 'method': '*', 'description': '成绩管理'},
    
    # ========== 财务管理 ==========
    {'name': '订单管理', 'code': 'order_management', 'api_path': '/api/finance/orders/', 'method': '*', 'description': '订单管理'},
    {'name': '退款管理', 'code': 'refund_management', 'api_path': '/api/finance/refunds/', 'method': '*', 'description': '退款管理'},
    
    # ========== 数据权限 ==========
    {'name': '查看本校数据', 'code': 'data_school', 'api_path': '*', 'method': '*', 'description': '查看本校数据'},
    {'name': '查看本班数据', 'code': 'data_class', 'api_path': '*', 'method': '*', 'description': '查看本班数据'},
    {'name': '查看自己数据', 'code': 'data_self', 'api_path': '*', 'method': '*', 'description': '查看自己数据'},
]


def init_permissions(self):
    self.stdout.write("开始初始化权限数据...")
    
    created_count = 0
    for perm_data in PERMISSIONS:
        perm, created = Permission.objects.get_or_create(
            code=perm_data['code'],
            defaults={
                'name': perm_data['name'],
                'api_path': perm_data.get('api_path', ''),
                'method': perm_data.get('method', ''),
                'description': perm_data.get('description', ''),
            }
        )
        if created:
            created_count += 1
            self.stdout.write(f"  创建权限: {perm.name} ({perm.code})")
    
    self.stdout.write(self.style.SUCCESS(f"权限初始化完成，共创建 {created_count} 个权限"))
    return created_count


def init_roles(self):
    self.stdout.write("\n开始初始化角色数据...")
    
    # 简化的角色权限映射
    role_permissions = {
        'admin': ['*'],  # 管理员拥有所有权限
        'teacher': [
            'course_management', 'class_management', 'schedule_management',
            'question_management', 'paper_management', 'exam_management', 'score_management',
            'data_class',  # 可查看本班数据
        ],
        'student_parent': [
            'score_management',  # 可查看成绩
            'data_self',  # 可查看自己数据
        ],
    }
    
    role_data = [
        {'name': '管理员', 'code': 'admin', 'description': '系统管理员，拥有所有权限'},
        {'name': '教师', 'code': 'teacher', 'description': '教师，可管理课程、考试、查看本班数据'},
        {'name': '学生/家长', 'code': 'student_parent', 'description': '学生/家长，可查看成绩和自己的信息'},
    ]
    
    created_count = 0
    for role_info in role_data:
        role, created = Role.objects.get_or_create(
            code=role_info['code'],
            defaults=role_info
        )
        if created:
            created_count += 1
            self.stdout.write(f"  创建角色: {role.name} ({role.code})")
            
            if role.code in role_permissions:
                perms = role_permissions[role.code]
                if perms == ['*']:
                    role.permissions.set(Permission.objects.all())
                else:
                    role.permissions.set(Permission.objects.filter(code__in=perms))
                role.save()
                self.stdout.write(f"    -> 已分配 {len(perms)} 个权限")
    
    self.stdout.write(self.style.SUCCESS(f"角色初始化完成，共创建 {created_count} 个角色"))
    return created_count


def assign_admin_permissions(self):
    self.stdout.write("\n为管理员用户分配角色...")
    
    try:
        admin = User.objects.get(username='admin')
        admin_role = Role.objects.get(code='admin')
        if admin_role not in admin.roles.all():
            admin.roles.add(admin_role)
            admin.save()
        self.stdout.write(f"  已为用户 {admin.username} 分配角色 {admin_role.name}")
    except User.DoesNotExist:
        self.stdout.write("  管理员用户不存在，跳过")
    except Role.DoesNotExist:
        self.stdout.write("  管理员角色不存在，跳过")


class Command(BaseCommand):
    help = '初始化权限系统和角色数据'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("=" * 50))
        self.stdout.write(self.style.NOTICE("开始权限系统初始化..."))
        self.stdout.write(self.style.NOTICE("=" * 50))
        
        init_permissions(self)
        init_roles(self)
        assign_admin_permissions(self)
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("权限系统初始化完成！"))
        self.stdout.write("=" * 50)