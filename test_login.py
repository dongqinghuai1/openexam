import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduadmin.settings')
import django
django.setup()

import requests
from users.authentication import generate_token
from users.models import User

def test_login(username, role_check):
    try:
        user = User.objects.get(username=username)
        token = generate_token(user.id, user.username)['access_token']
        headers = {'Authorization': f'Bearer {token}'}
        role_codes = [r.code for r in user.roles.all()]

        print(f'{username}:')
        print(f'  is_superuser: {user.is_superuser}')
        print(f'  角色: {role_codes}')
        passed = 'PASS' if role_check in role_codes else 'FAIL'
        print(f'  角色检查 ({role_check}): {passed}')

        r = requests.get('http://localhost:8000/api/users/me', headers=headers)
        print(f'  访问/api/users/me: {r.status_code}')
        return True
    except Exception as e:
        print(f'{username}: 错误 - {e}')
        return False

print('=' * 60)
print('测试各端用户登录:')
print('=' * 60)

test_login('admin', 'admin')
print()
test_login('teacher', 'teacher')
print()
test_login('qinghuai', 'student')