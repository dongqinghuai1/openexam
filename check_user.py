import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduadmin.settings')

import django
django.setup()

from users.models import User

user = User.objects.get(username='admin')
print('User:', user.username)
print('Is superuser:', user.is_superuser)
roles = user.roles.all()
print('Roles count:', roles.count())
for role in roles:
    print('Role:', role.name, role.code)