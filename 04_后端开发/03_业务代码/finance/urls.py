from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, RefundRecordViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'refunds', RefundRecordViewSet, basename='refund')

urlpatterns = [
    path('', include(router.urls)),
    path('orders/<int:pk>/apply_refund/', OrderViewSet.as_view({'post': 'apply_refund'}), name='order-apply-refund'),
]
