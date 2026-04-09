from rest_framework import serializers
from .models import User, Role, Permission, Menu, UserRole, Notification


class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'code', 'api_path', 'method', 'description']


class MenuSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Menu
        fields = ['id', 'name', 'path', 'component', 'icon', 'parent', 'sort', 'visible', 'permission', 'children']

    def get_children(self, obj):
        try:
            children = obj.children.filter(visible=True).order_by('sort')
            if not children.exists():
                return []
            return MenuSerializer(children, many=True).data
        except Exception:
            return []


class RoleSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Role
        fields = ['id', 'name', 'code', 'description', 'permissions', 'permission_ids', 'status', 'created_at']

    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        return role

    def update(self, instance, validated_data):
        permission_ids = validated_data.pop('permission_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)
        return instance


class UserSerializer(serializers.ModelSerializer):
    roles = RoleSerializer(many=True, read_only=True)
    role_ids = serializers.ListField(write_only=True, required=False)
    role_names = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone', 'avatar', 'gender', 'birthday', 'status', 'roles', 'role_ids', 'role_names', 'created_at']
        extra_kwargs = {'password': {'write_only': True}}

    def get_role_names(self, obj):
        return [role.name for role in obj.roles.all()]

    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        password = validated_data.pop('password', None)
        if validated_data.get('phone', '') == '':
            validated_data['phone'] = None
        if validated_data.get('email', '') == '':
            validated_data['email'] = None
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        if role_ids:
            roles = Role.objects.filter(id__in=role_ids)
            user.roles.set(roles)
        return user

    def update(self, instance, validated_data):
        role_ids = validated_data.pop('role_ids', None)
        password = validated_data.pop('password', None)
        if validated_data.get('phone', None) == '':
            validated_data['phone'] = None
        if validated_data.get('email', None) == '':
            validated_data['email'] = None
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        if role_ids is not None:
            roles = Role.objects.filter(id__in=role_ids)
            instance.roles.set(roles)
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'phone', 'gender', 'status', 'role_ids']

    def create(self, validated_data):
        role_ids = validated_data.pop('role_ids', [])
        password = validated_data.pop('password')
        if validated_data.get('phone', '') == '':
            validated_data['phone'] = None
        if validated_data.get('email', '') == '':
            validated_data['email'] = None
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        if role_ids:
            roles = Role.objects.filter(id__in=role_ids)
            user.roles.set(roles)
        return user


class NotificationSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('created_by', request.user)
        return super().create(validated_data)
