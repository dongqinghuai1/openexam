from django.core.management.base import BaseCommand

from edu.models import Subject


DEFAULT_SUBJECTS = [
    ('CHINESE', '语文'),
    ('MATH', '数学'),
    ('ENGLISH', '英语'),
    ('PHYSICS', '物理'),
    ('CHEMISTRY', '化学'),
    ('BIOLOGY', '生物'),
]


class Command(BaseCommand):
    help = 'Initialize default subjects if table is empty'

    def handle(self, *args, **options):
        if Subject.objects.exists():
            self.stdout.write(self.style.SUCCESS('Subjects already initialized'))
            return

        for index, (code, name) in enumerate(DEFAULT_SUBJECTS, start=1):
            Subject.objects.create(code=code, name=name, sort=index, status=True)

        self.stdout.write(self.style.SUCCESS(f'Created {len(DEFAULT_SUBJECTS)} default subjects'))
