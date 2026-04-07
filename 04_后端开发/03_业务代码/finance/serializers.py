from rest_framework import serializers
from .models import Order, PaymentRecord, RefundRecord


class OrderSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.name', read_only=True)
    student_phone = serializers.CharField(source='student.phone', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    package_name = serializers.CharField(source='course_package.name', read_only=True)
    creator_name = serializers.CharField(source='created_by.username', read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def create(self, validated_data):
        from datetime import datetime
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        return Order.objects.create(order_no=order_no, **validated_data)


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