import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduadmin.settings')
import django
django.setup()

from django.db.models import Count
from users.models import User

print('=== 检查重复数据 ===')

# 查找重复的用户名
print('\n重复的用户名:')
dup_usernames = User.objects.values('username').annotate(count=Count('id')).filter(count__gt=1)
for dup in dup_usernames:
    print(f"  用户名 '{dup['username']}' 出现 {dup['count']} 次")
    users = User.objects.filter(username=dup['username'])
    for u in users:
        print(f'    - ID: {u.id}, username: {u.username}, is_superuser: {u.is_superuser}')

# 查找重复的手机号
print('\n重复的手机号:')
dup_phones = User.objects.exclude(phone='').exclude(phone__isnull=True).values('phone').annotate(count=Count('id')).filter(count__gt=1)
for dup in dup_phones:
    print(f"  手机号 '{dup['phone']}' 出现 {dup['count']} 次")

# 查找重复的邮箱
print('\n重复的邮箱:')
dup_emails = User.objects.exclude(email='').exclude(email__isnull=True).values('email').annotate(count=Count('id')).filter(count__gt=1)
for dup in dup_emails:
    print(f"  邮箱 '{dup['email']}' 出现 {dup['count']} 次")

print('\n总用户数:', User.objects.count())