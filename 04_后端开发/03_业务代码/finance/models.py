from django.db import models
from django.conf import settings
from edu.models import Student, Course, CoursePackage


class Order(models.Model):
    """订单模型"""
    ORDER_NO_PREFIX = 'ORD'

    order_no = models.CharField(max_length=50, unique=True, verbose_name='订单号')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='学生', related_name='orders')
    course = models.ForeignKey(Course, on_delete=models.PROTECT, verbose_name='课程', null=True, blank=True)
    course_package = models.ForeignKey(CoursePackage, on_delete=models.SET_NULL, verbose_name='课程包', null=True, blank=True)
    quantity = models.IntegerField(default=1, verbose_name='课时数')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='订单金额')
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='优惠金额')
    final_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='实收金额')
    payment_type = models.CharField(max_length=20, choices=[('wechat', '微信'), ('alipay', '支付宝'), ('offline', '线下')], verbose_name='支付方式')
    status = models.CharField(max_length=20, default='pending', choices=[('pending', '待支付'), ('paid', '已支付'), ('cancelled', '已取消'), ('refunded', '已退款')], verbose_name='状态')
    expired_at = models.DateTimeField(verbose_name='过期时间')
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='创建人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'tb_order'
        verbose_name = '订单'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_no


class PaymentRecord(models.Model):
    """支付记录"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单', related_name='payment_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='支付金额')
    payment_type = models.CharField(max_length=20, verbose_name='支付方式')
    transaction_id = models.CharField(max_length=100, verbose_name='第三方流水号', blank=True)
    status = models.CharField(max_length=20, choices=[('success', '成功'), ('failed', '失败')], verbose_name='状态')
    paid_at = models.DateTimeField(verbose_name='支付时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_payment_record'
        verbose_name = '支付记录'
        verbose_name_plural = verbose_name


class RefundRecord(models.Model):
    """退款记录"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='订单', related_name='refund_records')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='退款金额')
    reason = models.TextField(verbose_name='退款原因')
    status = models.CharField(max_length=20, default='pending', choices=[('pending', '待审批'), ('approved', '已批准'), ('rejected', '已拒绝')], verbose_name='状态')
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='申请人', related_name='refund_applicants')
    approver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='审批人', related_name='refund_approvers')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'tb_refund_record'
        verbose_name = '退款记录'
        verbose_name_plural = verbose_name