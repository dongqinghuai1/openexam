import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduadmin.settings')

import django
django.setup()

import requests
from users.authentication import generate_token

# 登录获取token
login_url = 'http://localhost:8000/api/users/login'
login_data = {'username': 'admin', 'password': 'admin123'}
login_response = requests.post(login_url, json=login_data)
print('Login status:', login_response.status_code)
print('Login response:', login_response.json())

token = login_response.json().get('token')
print('Token:', token[:50] + '...')

# 使用token访问API
headers = {'Authorization': f'Bearer {token}'}

modules = [
    '/api/users/roles/',
    '/api/edu/students/',
    '/api/edu/teachers/',
    '/api/edu/classes/',
    '/api/edu/courses/',
    '/api/exam/questions/',
    '/api/exam/papers/',
    '/api/finance/orders/',
]

print('\nTesting API access:')
for m in modules:
    r = requests.get(f'http://localhost:8000{m}', headers=headers)
    print(f'{m}: {r.status_code}')