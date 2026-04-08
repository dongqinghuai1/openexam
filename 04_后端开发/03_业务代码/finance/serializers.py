from rest_framework import serializers
from .models import Order, PaymentRecord, RefundRecord
from django.utils import timezone


class OrderSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_phone = serializers.CharField(source='student.phone', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    package_name = serializers.CharField(source='course_package.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.username', read_only=True)
    order_no = serializers.CharField(read_only=True)
    expired_at = serializers.DateTimeField(required=False)
    final_amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        from datetime import datetime
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        validated_data.setdefault('discount', 0)
        amount = validated_data.get('amount', 0)
        discount = validated_data.get('discount', 0)
        validated_data['final_amount'] = validated_data.get('final_amount') or amount - discount
        validated_data['expired_at'] = validated_data.get('expired_at') or timezone.now() + timezone.timedelta(days=1)
        return Order.objects.create(order_no=order_no, **validated_data)

    def validate(self, attrs):
        amount = attrs.get('amount') or getattr(self.instance, 'amount', 0)
        discount = attrs.get('discount', getattr(self.instance, 'discount', 0)) or 0
        final_amount = attrs.get('final_amount', getattr(self.instance, 'final_amount', None))
        if final_amount is None:
            final_amount = amount - discount
            attrs['final_amount'] = final_amount
        if final_amount < 0:
            raise serializers.ValidationError({'final_amount': '实收金额不能小于 0'})
        if not attrs.get('course') and not attrs.get('course_package') and not getattr(self.instance, 'course', None) and not getattr(self.instance, 'course_package', None):
            raise serializers.ValidationError({'course': '课程和课程包至少选择一个'})
        return attrs


class PaymentRecordSerializer(serializers.ModelSerializer):
    order_no = serializers.CharField(source='order.order_no', read_only=True)

    class Meta:
        model = PaymentRecord
        fields = '__all__'


class RefundRecordSerializer(serializers.ModelSerializer):
    applicant_name = serializers.CharField(source='applicant.username', read_only=True)
    approver_name = serializers.CharField(source='approver.username', read_only=True)
    order_no = serializers.CharField(source='order.order_no', read_only=True)
    student_name = serializers.CharField(source='order.student.name', read_only=True)

    class Meta:
        model = RefundRecord
        fields = '__all__'
        read_only_fields = ['applicant', 'approver']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            validated_data.setdefault('applicant', request.user)
        return super().create(validated_data)
