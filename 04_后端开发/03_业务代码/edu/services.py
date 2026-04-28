from decimal import Decimal


class HoursService:
    """课时服务类

    提供课时扣减、赠送、冻结、解冻等操作的统一实现。
    """

    @staticmethod
    def deduct_hours(schedule, operator=None):
        """扣减班级下所有在校学生的1课时

        Args:
            schedule: Schedule 实例
            operator: 操作人用户，None 表示系统自动扣课
        """
        from .models import StudentHoursAccount, HoursFlow

        class_students = schedule.edu_class.class_students.filter(status='studying')
        for cs in class_students:
            try:
                account = StudentHoursAccount.objects.get(
                    student=cs.student,
                    course=schedule.course,
                    status='active'
                )
            except StudentHoursAccount.DoesNotExist:
                continue

            if HoursFlow.objects.filter(account=account, schedule=schedule, type='deduct').exists():
                continue

            before = account.remaining_hours
            account.used_hours += Decimal('1.0')
            account.save(update_fields=['used_hours', 'updated_at'])

            HoursFlow.objects.create(
                account=account,
                schedule=schedule,
                type='deduct',
                hours=Decimal('1.0'),
                balance_before=before,
                balance_after=account.remaining_hours,
                note=f'上课扣课 - {schedule.date}',
                operator=operator,
            )

    @staticmethod
    def add_flow(account, flow_type, hours, note, operator=None):
        """记录课时流水

        Args:
            account: StudentHoursAccount 实例
            flow_type: 流水类型 (gift/freeze/unfreeze)
            hours: 课时数量
            note: 备注
            operator: 操作人
        """
        from .models import HoursFlow

        before = account.remaining_hours
        HoursFlow.objects.create(
            account=account,
            type=flow_type,
            hours=hours,
            balance_before=before,
            balance_after=account.remaining_hours,
            note=note,
            operator=operator,
        )
