import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduadmin.settings')
import django
django.setup()

from users.models import User

print('=== 所有用户列表 ===')
for u in User.objects.all():
    print(f'ID: {u.id}, username: {u.username}, phone: {u.phone}, email: {u.email}')