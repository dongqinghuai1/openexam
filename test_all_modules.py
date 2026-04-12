import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduadmin.settings')

import django
django.setup()

import requests
from users.authentication import generate_token

token = generate_token(1, 'admin')['access_token']
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

for m in modules:
    try:
        r = requests.get(f'http://localhost:8000{m}', headers=headers)
        print(f'{m}: {r.status_code}')
    except Exception as e:
        print(f'{m}: Error - {e}')