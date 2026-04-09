from datetime import date, time, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import User
from edu.models import Subject, Course, Teacher, Student, EduClass, ClassStudent, Schedule


class Command(BaseCommand):
    help = 'Initialize demo teacher, student, and parent users with minimal edu data'

    def handle(self, *args, **options):
        subject, _ = Subject.objects.get_or_create(code='OPENEXAM_CHINESE', defaults={'name': '语文', 'sort': 99, 'status': True})
        course, _ = Course.objects.get_or_create(
            code='OPENEXAM_COURSE_001',
            defaults={
                'name': 'OPENEXAM 演示课程',
                'subject': subject,
                'description': '用于教师端、学生端、家长端联调的演示课程',
                'total_hours': 20,
                'duration': 90,
                'price': 1999,
                'status': 'active',
            }
        )

        teacher_user, _ = self._ensure_user(
            username='teacher',
            password='teacher123',
            phone='13800000001',
            email='teacher@openexam.local',
        )
        student_user, _ = self._ensure_user(
            username='13800000002',
            password='student123',
            phone='13800000002',
            email='student@openexam.local',
        )
        parent_user, _ = self._ensure_user(
            username='13800000003',
            password='parent123',
            phone='13800000003',
            email='parent@openexam.local',
        )

        teacher, _ = Teacher.objects.get_or_create(
            phone='13800000001',
            defaults={
                'name': '王老师',
                'gender': 'male',
                'education': '本科',
                'major': '汉语言文学',
                'certification': '教师资格证',
                'status': 'active',
                'hire_date': date.today() - timedelta(days=180),
                'salary_type': 'hourly',
            }
        )
        teacher.subjects.add(subject)

        student, _ = Student.objects.get_or_create(
            phone='13800000002',
            defaults={
                'name': '李同学',
                'gender': 'female',
                'grade': '初二',
                'school': 'OPENEXAM 实验学校',
                'parent_name': '李家长',
                'parent_phone': '13800000003',
                'status': 'active',
                'enrollment_date': date.today() - timedelta(days=60),
            }
        )

        edu_class, _ = EduClass.objects.get_or_create(
            code='OPENEXAM_CLASS_001',
            defaults={
                'name': 'OPENEXAM 精品班',
                'course': course,
                'teacher': teacher,
                'max_students': 20,
                'status': 'open',
                'start_date': date.today() - timedelta(days=30),
            }
        )

        ClassStudent.objects.get_or_create(
            edu_class=edu_class,
            student=student,
            defaults={'join_date': date.today() - timedelta(days=30), 'status': 'studying'}
        )

        today = date.today()
        for day_offset in range(0, 3):
            Schedule.objects.get_or_create(
                edu_class=edu_class,
                teacher=teacher,
                course=course,
                date=today + timedelta(days=day_offset),
                start_time=time(19, 0),
                end_time=time(20, 30),
                defaults={
                    'room': 'ONLINE-ROOM-1',
                    'status': 'scheduled',
                    'note': 'OPENEXAM 用户端演示课次',
                    'created_by': teacher_user,
                }
            )

        self.stdout.write(self.style.SUCCESS('Initialized demo users and edu data:'))
        self.stdout.write(self.style.SUCCESS('teacher / teacher123'))
        self.stdout.write(self.style.SUCCESS('13800000002 / student123'))
        self.stdout.write(self.style.SUCCESS('13800000003 / parent123'))

    def _ensure_user(self, username, password, phone, email):
        user = User.objects.filter(username=username).first()
        created = False
        if not user:
            user = User(username=username, phone=phone, email=email, status='active')
            user.set_password(password)
            user.save()
            created = True
        else:
            changed = False
            if user.phone != phone:
                user.phone = phone
                changed = True
            if user.email != email:
                user.email = email
                changed = True
            if user.status != 'active':
                user.status = 'active'
                changed = True
            if changed:
                user.save(update_fields=['phone', 'email', 'status'])
        return user, created
