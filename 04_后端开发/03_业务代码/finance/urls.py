from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, RefundRecordViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'refunds', RefundRecordViewSet, basename='refund')

urlpatterns = [
    path('', include(router.urls)),
]