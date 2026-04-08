from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from datetime import datetime
from .models import Order, PaymentRecord, RefundRecord
from .serializers import OrderSerializer, PaymentRecordSerializer, RefundRecordSerializer
from edu.models import StudentHoursAccount


class OrderViewSet(viewsets.ModelViewSet):
    """订单管理视图"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['student', 'status', 'payment_type']
    search_fields = ['order_no', 'student__name']

    def perform_create(self, serializer):
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}"
        serializer.save(order_no=order_no, created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def pay(self, request, pk=None):
        """支付订单"""
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        # TODO: 调用支付接口
        order.status = 'paid'
        order.paid_at = timezone.now()
        order.save()

        # 创建课时账户
        StudentHoursAccount.objects.create(
            student=order.student,
            course=order.course,
            total_hours=order.quantity,
            expire_date=timezone.now().date() + timezone.timedelta(days=365)
        )

        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """取消订单"""
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': '订单状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        order.status = 'cancelled'
        order.save()
        return Response(OrderSerializer(order).data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """订单统计"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        queryset = self.get_queryset().filter(status='paid')

        if start_date and end_date:
            queryset = queryset.filter(paid_at__range=[start_date, end_date])

        total = queryset.aggregate(total=Sum('final_amount'))['total'] or 0
        count = queryset.count()

        return Response({
            'total_amount': total,
            'order_count': count
        })


class RefundRecordViewSet(viewsets.ModelViewSet):
    """退款管理视图"""
    queryset = RefundRecord.objects.all()
    serializer_class = RefundRecordSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'order']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """审批退款"""
        refund = self.get_object()
        if refund.status != 'pending':
            return Response({'error': '退款状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        refund.status = 'approved'
        refund.approver = request.user
        refund.save()

        # 冻结课时
        accounts = StudentHoursAccount.objects.filter(student=refund.order.student, course=refund.order.course)
        for account in accounts:
            account.frozen_hours += refund.order.quantity
            account.save()

        # 更新订单状态
        refund.order.status = 'refunded'
        refund.order.save()

        return Response(RefundRecordSerializer(refund).data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """拒绝退款"""
        refund = self.get_object()
        if refund.status != 'pending':
            return Response({'error': '退款状态不正确'}, status=status.HTTP_400_BAD_REQUEST)

        refund.status = 'rejected'
        refund.approver = request.user
        refund.save()

        return Response(RefundRecordSerializer(refund).data)