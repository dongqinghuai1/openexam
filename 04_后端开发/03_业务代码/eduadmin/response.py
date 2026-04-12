"""
统一API响应格式和全局异常处理
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import IntegrityError
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)


class APIResponse:
    """统一API响应格式"""
    
    @staticmethod
    def success(data=None, message='操作成功', code=200):
        """成功响应"""
        return Response({
            'code': code,
            'message': message,
            'data': data
        }, status=status.HTTP_200_OK)
    
    @staticmethod
    def error(message='操作失败', code=400, errors=None):
        """错误响应"""
        response_data = {
            'code': code,
            'message': message,
        }
        if errors:
            response_data['errors'] = errors
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    @staticmethod
    def unauthorized(message='未授权'):
        """未授权响应"""
        return Response({
            'code': 401,
            'message': message,
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @staticmethod
    def forbidden(message='权限不足'):
        """禁止访问响应"""
        return Response({
            'code': 403,
            'message': message,
        }, status=status.HTTP_403_FORBIDDEN)
    
    @staticmethod
    def not_found(message='资源不存在'):
        """未找到响应"""
        return Response({
            'code': 404,
            'message': message,
        }, status=status.HTTP_404_NOT_FOUND)


def custom_exception_handler(exc, context):
    """
    自定义全局异常处理器
    统一API响应格式
    """
    # 调用DRF默认的异常处理器
    response = exception_handler(exc, context)
    
    if response is not None:
        # 处理DRF的异常
        if response.status_code == 400:
            # 检查是否是ValidationError
            if isinstance(response.data, dict):
                errors = {}
                for key, value in response.data.items():
                    if isinstance(value, list):
                        errors[key] = value[0] if value else '无效的值'
                    else:
                        errors[key] = str(value)
                response.data = {
                    'code': 400,
                    'message': '参数验证失败',
                    'errors': errors
                }
            elif isinstance(response.data, list):
                response.data = {
                    'code': 400,
                    'message': response.data[0] if response.data else '参数验证失败',
                    'errors': response.data
                }
        elif response.status_code == 401:
            response.data = {
                'code': 401,
                'message': response.data.get('detail', '未授权，请登录'),
            }
        elif response.status_code == 403:
            response.data = {
                'code': 403,
                'message': response.data.get('detail', '权限不足'),
            }
        elif response.status_code == 404:
            response.data = {
                'code': 404,
                'message': response.data.get('detail', '资源不存在'),
            }
        return response
    
    # 处理Django数据库异常
    if isinstance(exc, IntegrityError):
        logger.error(f"数据库完整性错误: {exc}")
        return APIResponse.error(
            message='数据冲突，请检查是否重复',
            code=409
        )
    
    # 处理Django验证异常
    if isinstance(exc, ValidationError):
        logger.error(f"验证错误: {exc}")
        return APIResponse.error(
            message=str(exc),
            code=400
        )
    
    # 处理其他未捕获的异常
    logger.error(f"未处理的异常: {type(exc).__name__}: {exc}")
    return APIResponse.error(
        message='服务器内部错误',
        code=500
    )