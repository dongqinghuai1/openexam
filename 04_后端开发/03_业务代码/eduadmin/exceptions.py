from django.db import IntegrityError
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, IntegrityError):
        return Response({'error': '数据唯一性冲突，请检查重复项后重试'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'error': '服务器内部错误，请根据页面提示检查输入或稍后重试'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
