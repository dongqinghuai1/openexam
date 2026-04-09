from datetime import date
import random

from django.core.cache import cache
from django.core.mail import send_mail
from django.conf import settings

from edu.models import Teacher, Student
from users.models import Role, User


VERIFY_CODE_TTL = 300


def build_verify_cache_key(scene: str, email: str) -> str:
    return f'email_code:{scene}:{email}'


def generate_verify_code() -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(6))


def store_verify_code(scene: str, email: str, code: str):
    cache.set(build_verify_cache_key(scene, email), code, timeout=VERIFY_CODE_TTL)


def verify_code(scene: str, email: str, code: str) -> bool:
    cached = cache.get(build_verify_cache_key(scene, email))
    return bool(cached and cached == code)


def clear_verify_code(scene: str, email: str):
    cache.delete(build_verify_cache_key(scene, email))


def send_email_code(email: str, code: str, scene_text: str):
    if not settings.EMAIL_HOST or not settings.DEFAULT_FROM_EMAIL:
        raise RuntimeError('邮箱配置不完整，请检查 SMTP 环境变量')

    subject = f'OPENEXAM {scene_text}验证码'
    message = f'您的验证码是 {code}，5 分钟内有效，用于{scene_text}。若非本人操作，请忽略此邮件。'
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [email], fail_silently=False)


def ensure_role(code: str, name: str):
    role = Role.objects.filter(code=code).first()
    if role:
        return role
    return Role.objects.create(code=code, name=name, status=True)


def create_related_profile(user: User, role_code: str, extra: dict):
    if role_code == 'student':
        Student.objects.get_or_create(
            phone=user.phone,
            defaults={
                'name': extra.get('name') or user.username,
                'grade': extra.get('grade') or '未设置',
                'school': extra.get('school') or '',
                'parent_name': extra.get('parent_name') or '未设置',
                'parent_phone': extra.get('parent_phone') or user.phone,
                'status': 'active',
                'enrollment_date': date.today(),
            }
        )
    elif role_code == 'teacher':
        Teacher.objects.get_or_create(
            phone=user.phone,
            defaults={
                'name': extra.get('name') or user.username,
                'education': extra.get('education') or '待完善',
                'major': extra.get('major') or '待完善',
                'certification': extra.get('certification') or '',
                'status': 'active' if user.status == 'active' else 'resigned',
                'hire_date': date.today(),
                'salary_type': 'hourly',
            }
        )
