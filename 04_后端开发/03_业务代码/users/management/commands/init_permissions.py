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


PERMISSIONS = [
    # ========== 系统管理模块 ==========
    {'name': '用户管理', 'code': 'user_management', 'api_path': '/api/users/', 'method': 'GET', 'description': '查看用户列表'},
    {'name': '用户创建', 'code': 'user_create', 'api_path': '/api/users/', 'method': 'POST', 'description': '创建用户'},
    {'name': '用户编辑', 'code': 'user_edit', 'api_path': '/api/users/', 'method': 'PUT', 'description': '编辑用户'},
    {'name': '用户删除', 'code': 'user_delete', 'api_path': '/api/users/', 'method': 'DELETE', 'description': '删除用户'},
    
    {'name': '角色管理', 'code': 'role_management', 'api_path': '/api/users/roles/', 'method': 'GET', 'description': '查看角色列表'},
    {'name': '角色创建', 'code': 'role_create', 'api_path': '/api/users/roles/', 'method': 'POST', 'description': '创建角色'},
    {'name': '角色编辑', 'code': 'role_edit', 'api_path': '/api/users/roles/', 'method': 'PUT', 'description': '编辑角色'},
    {'name': '角色删除', 'code': 'role_delete', 'api_path': '/api/users/roles/', 'method': 'DELETE', 'description': '删除角色'},
    {'name': '角色分配权限', 'code': 'role_assign_permissions', 'api_path': '/api/users/roles/', 'method': 'PATCH', 'description': '为角色分配权限'},
    
    {'name': '菜单管理', 'code': 'menu_management', 'api_path': '/api/users/menus/', 'method': 'GET', 'description': '查看菜单列表'},
    {'name': '菜单创建', 'code': 'menu_create', 'api_path': '/api/users/menus/', 'method': 'POST', 'description': '创建菜单'},
    {'name': '菜单编辑', 'code': 'menu_edit', 'api_path': '/api/users/menus/', 'method': 'PUT', 'description': '编辑菜单'},
    {'name': '菜单删除', 'code': 'menu_delete', 'api_path': '/api/users/menus/', 'method': 'DELETE', 'description': '删除菜单'},
    
    {'name': '权限管理', 'code': 'permission_management', 'api_path': '/api/users/permissions/', 'method': 'GET', 'description': '查看权限列表'},
    {'name': '操作日志', 'code': 'log_management', 'api_path': '/api/users/operation-logs/', 'method': 'GET', 'description': '查看操作日志'},
    {'name': '通知管理', 'code': 'notification_management', 'api_path': '/api/users/notifications/', 'method': 'GET', 'description': '查看通知列表'},
    
    # ========== 教务管理模块 ==========
    {'name': '学生管理', 'code': 'student_management', 'api_path': '/api/edu/students/', 'method': 'GET', 'description': '查看学生列表'},
    {'name': '学生创建', 'code': 'student_create', 'api_path': '/api/edu/students/', 'method': 'POST', 'description': '创建学生'},
    {'name': '学生编辑', 'code': 'student_edit', 'api_path': '/api/edu/students/', 'method': 'PUT', 'description': '编辑学生'},
    {'name': '学生删除', 'code': 'student_delete', 'api_path': '/api/edu/students/', 'method': 'DELETE', 'description': '删除学生'},
    
    {'name': '教师管理', 'code': 'teacher_management', 'api_path': '/api/edu/teachers/', 'method': 'GET', 'description': '查看教师列表'},
    {'name': '教师创建', 'code': 'teacher_create', 'api_path': '/api/edu/teachers/', 'method': 'POST', 'description': '创建教师'},
    {'name': '教师编辑', 'code': 'teacher_edit', 'api_path': '/api/edu/teachers/', 'method': 'PUT', 'description': '编辑教师'},
    {'name': '教师删除', 'code': 'teacher_delete', 'api_path': '/api/edu/teachers/', 'method': 'DELETE', 'description': '删除教师'},
    
    {'name': '课程管理', 'code': 'course_management', 'api_path': '/api/edu/courses/', 'method': 'GET', 'description': '查看课程列表'},
    {'name': '课程创建', 'code': 'course_create', 'api_path': '/api/edu/courses/', 'method': 'POST', 'description': '创建课程'},
    {'name': '课程编辑', 'code': 'course_edit', 'api_path': '/api/edu/courses/', 'method': 'PUT', 'description': '编辑课程'},
    {'name': '课程删除', 'code': 'course_delete', 'api_path': '/api/edu/courses/', 'method': 'DELETE', 'description': '删除课程'},
    
    {'name': '班级管理', 'code': 'class_management', 'api_path': '/api/edu/classes/', 'method': 'GET', 'description': '查看班级列表'},
    {'name': '班级创建', 'code': 'class_create', 'api_path': '/api/edu/classes/', 'method': 'POST', 'description': '创建班级'},
    {'name': '班级编辑', 'code': 'class_edit', 'api_path': '/api/edu/classes/', 'method': 'PUT', 'description': '编辑班级'},
    {'name': '班级删除', 'code': 'class_delete', 'api_path': '/api/edu/classes/', 'method': 'DELETE', 'description': '删除班级'},
    
    {'name': '排课管理', 'code': 'schedule_management', 'api_path': '/api/edu/schedules/', 'method': 'GET', 'description': '查看排课列表'},
    {'name': '排课创建', 'code': 'schedule_create', 'api_path': '/api/edu/schedules/', 'method': 'POST', 'description': '创建排课'},
    {'name': '排课编辑', 'code': 'schedule_edit', 'api_path': '/api/edu/schedules/', 'method': 'PUT', 'description': '编辑排课'},
    {'name': '排课删除', 'code': 'schedule_delete', 'api_path': '/api/edu/schedules/', 'method': 'DELETE', 'description': '删除排课'},
    
    {'name': '调课管理', 'code': 'reschedule_management', 'api_path': '/api/edu/reschedules/', 'method': 'GET', 'description': '查看调课记录'},
    {'name': '请假管理', 'code': 'leave_management', 'api_path': '/api/edu/leaves/', 'method': 'GET', 'description': '查看请假记录'},
    {'name': '课时账户管理', 'code': 'hours_account_management', 'api_path': '/api/edu/student-hours/', 'method': 'GET', 'description': '查看课时账户'},
    {'name': '课时流水查看', 'code': 'hours_flow_view', 'api_path': '/api/edu/hours-flows/', 'method': 'GET', 'description': '查看课时流水'},
    
    # ========== 考试管理模块 ==========
    {'name': '题库管理', 'code': 'question_management', 'api_path': '/api/exam/questions/', 'method': 'GET', 'description': '查看题库列表'},
    {'name': '题目创建', 'code': 'question_create', 'api_path': '/api/exam/questions/', 'method': 'POST', 'description': '创建题目'},
    {'name': '题目编辑', 'code': 'question_edit', 'api_path': '/api/exam/questions/', 'method': 'PUT', 'description': '编辑题目'},
    {'name': '题目删除', 'code': 'question_delete', 'api_path': '/api/exam/questions/', 'method': 'DELETE', 'description': '删除题目'},
    {'name': '题目导入', 'code': 'question_import', 'api_path': '/api/exam/questions/import/', 'method': 'POST', 'description': '导入题目'},
    {'name': '题目导出', 'code': 'question_export', 'api_path': '/api/exam/questions/export/', 'method': 'GET', 'description': '导出题目'},
    
    {'name': '试卷管理', 'code': 'paper_management', 'api_path': '/api/exam/papers/', 'method': 'GET', 'description': '查看试卷列表'},
    {'name': '试卷创建', 'code': 'paper_create', 'api_path': '/api/exam/papers/', 'method': 'POST', 'description': '创建试卷'},
    {'name': '试卷编辑', 'code': 'paper_edit', 'api_path': '/api/exam/papers/', 'method': 'PUT', 'description': '编辑试卷'},
    {'name': '试卷删除', 'code': 'paper_delete', 'api_path': '/api/exam/papers/', 'method': 'DELETE', 'description': '删除试卷'},
    
    {'name': '考试管理', 'code': 'exam_management', 'api_path': '/api/exam/exams/', 'method': 'GET', 'description': '查看考试列表'},
    {'name': '考试创建', 'code': 'exam_create', 'api_path': '/api/exam/exams/', 'method': 'POST', 'description': '创建考试'},
    {'name': '考试编辑', 'code': 'exam_edit', 'api_path': '/api/exam/exams/', 'method': 'PUT', 'description': '编辑考试'},
    {'name': '考试删除', 'code': 'exam_delete', 'api_path': '/api/exam/exams/', 'method': 'DELETE', 'description': '删除考试'},
    {'name': '考试发布', 'code': 'exam_publish', 'api_path': '/api/exam/exams/publish/', 'method': 'POST', 'description': '发布考试'},
    
    {'name': '成绩查看', 'code': 'score_view', 'api_path': '/api/exam/scores/', 'method': 'GET', 'description': '查看成绩列表'},
    {'name': '成绩批改', 'code': 'score_correct', 'api_path': '/api/exam/exams/', 'method': 'PATCH', 'description': '批改主观题'},
    
    # ========== 财务管理模块 ==========
    {'name': '订单管理', 'code': 'order_management', 'api_path': '/api/finance/orders/', 'method': 'GET', 'description': '查看订单列表'},
    {'name': '订单创建', 'code': 'order_create', 'api_path': '/api/finance/orders/', 'method': 'POST', 'description': '创建订单'},
    {'name': '订单编辑', 'code': 'order_edit', 'api_path': '/api/finance/orders/', 'method': 'PUT', 'description': '编辑订单'},
    {'name': '订单删除', 'code': 'order_delete', 'api_path': '/api/finance/orders/', 'method': 'DELETE', 'description': '删除订单'},
    {'name': '订单支付', 'code': 'order_pay', 'api_path': '/api/finance/orders/pay/', 'method': 'POST', 'description': '支付订单'},
    
    {'name': '退款管理', 'code': 'refund_management', 'api_path': '/api/finance/refunds/', 'method': 'GET', 'description': '查看退款列表'},
    {'name': '退款创建', 'code': 'refund_create', 'api_path': '/api/finance/refunds/', 'method': 'POST', 'description': '申请退款'},
    {'name': '退款审批', 'code': 'refund_approve', 'api_path': '/api/finance/refunds/', 'method': 'PATCH', 'description': '审批退款'},
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
    
    role_permissions = {
        'admin': ['*'],
        'edu_admin': [
            'student_management', 'student_create', 'student_edit', 'student_delete',
            'teacher_management', 'teacher_create', 'teacher_edit', 'teacher_delete',
            'course_management', 'course_create', 'course_edit', 'course_delete',
            'class_management', 'class_create', 'class_edit', 'class_delete',
            'schedule_management', 'schedule_create', 'schedule_edit', 'schedule_delete',
            'reschedule_management', 'leave_management', 'hours_account_management', 'hours_flow_view',
            'question_management', 'question_create', 'question_edit', 'question_delete', 'question_import', 'question_export',
            'paper_management', 'paper_create', 'paper_edit', 'paper_delete',
            'exam_management', 'exam_create', 'exam_edit', 'exam_delete', 'exam_publish',
            'score_view', 'score_correct',
        ],
        'teacher': [
            'question_management', 'question_create', 'question_edit',
            'paper_management', 'paper_create', 'paper_edit', 'paper_delete',
            'exam_management', 'exam_create', 'exam_edit', 'exam_delete', 'exam_publish',
            'score_view', 'score_correct',
            'schedule_management',
            'leave_management',
        ],
        'student_parent': [
            'score_view',
        ],
        'finance_admin': [
            'order_management', 'order_create', 'order_edit', 'order_delete', 'order_pay',
            'refund_management', 'refund_create', 'refund_approve',
        ],
    }
    
    role_data = [
        {'name': '系统管理员', 'code': 'admin', 'description': '拥有系统所有权限'},
        {'name': '教务管理员', 'code': 'edu_admin', 'description': '负责教务管理工作'},
        {'name': '教师', 'code': 'teacher', 'description': '负责教学和考试工作'},
        {'name': '学生/家长', 'code': 'student_parent', 'description': '查看成绩等'},
        {'name': '财务管理员', 'code': 'finance_admin', 'description': '负责财务管理工作'},
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