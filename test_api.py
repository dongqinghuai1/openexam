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
print('Token:', token)

# 使用token访问API
roles_url = 'http://localhost:8000/api/users/roles/'
headers = {'Authorization': f'Bearer {token}'}
roles_response = requests.get(roles_url, headers=headers)
print('Roles status:', roles_response.status_code)
print('Roles response:', roles_response.text)