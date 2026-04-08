from django.core.management.base import BaseCommand
from users.models import User


class Command(BaseCommand):
    help = 'Initialize default admin user if missing'

    def add_arguments(self, parser):
        parser.add_argument('--username', default='admin')
        parser.add_argument('--password', default='admin123')
        parser.add_argument('--email', default='admin@example.com')

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']

        user = User.objects.filter(username=username).first()
        if user:
            if not user.is_superuser or not user.is_staff:
                user.is_superuser = True
                user.is_staff = True
                user.status = 'active'
                user.save(update_fields=['is_superuser', 'is_staff', 'status'])
            self.stdout.write(self.style.SUCCESS(f'Admin user already exists: {username}'))
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            status='active',
        )
        self.stdout.write(self.style.SUCCESS(f'Created default admin user: {username}'))
