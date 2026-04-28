from rest_framework import status
from rest_framework.response import Response


class RolePermissionMixin:
    """用户角色权限工具混入类

    提供获取用户角色信息的方法，供 ViewSet 查询过滤使用。
    """

    def _get_user_phone(self, user):
        return getattr(user, 'phone', None) or getattr(user, 'username', None)

    def _get_role_codes(self, user):
        return set(user.roles.values_list('code', flat=True))

    def _get_role_names(self, user):
        return set(user.roles.values_list('name', flat=True))

    def _is_admin(self, user):
        role_codes = self._get_role_codes(user)
        role_names = self._get_role_names(user)
        return user.is_superuser or 'admin' in role_codes or '管理员' in role_names


class ApprovalActionMixin:
    """审批动作混入类

    提供 approve/reject 审批方法，供调课记录、请假记录等视图集使用。
    """

    def approve(self, request, pk=None):
        record = self.get_object()
        if record.status != 'pending':
            return Response({'error': '当前记录不可审批'}, status=status.HTTP_400_BAD_REQUEST)
        record.status = 'approved'
        record.approver = request.user
        record.save(update_fields=['status', 'approver'])
        return Response(self.get_serializer(record).data)

    def reject(self, request, pk=None):
        record = self.get_object()
        if record.status != 'pending':
            return Response({'error': '当前记录不可审批'}, status=status.HTTP_400_BAD_REQUEST)
        record.status = 'rejected'
        record.approver = request.user
        record.save(update_fields=['status', 'approver'])
        return Response(self.get_serializer(record).data)
