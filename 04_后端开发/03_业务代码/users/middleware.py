import time

from .models import OperationLog


class OperationLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.time()
        response = self.get_response(request)

        if request.path.startswith('/api/') and request.method in ['POST', 'PUT', 'DELETE']:
            try:
                body = request.body.decode('utf-8')[:2000] if request.body else ''
            except Exception:
                body = ''

            response_text = ''
            try:
                if hasattr(response, 'content'):
                    response_text = response.content.decode('utf-8')[:2000]
            except Exception:
                response_text = ''

            user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
            OperationLog.objects.create(
                user=user,
                username=user.username if user else 'anonymous',
                method=request.method,
                path=request.path,
                body=body,
                response=response_text,
                ip=request.META.get('REMOTE_ADDR'),
                duration=int((time.time() - start) * 1000),
            )

        return response
