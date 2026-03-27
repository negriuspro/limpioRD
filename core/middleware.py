# core/middleware.py
from .signals import _thread_locals

class AuditUserMiddleware:
    """Captura el usuario actual para usarlo en Auditoría."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            _thread_locals.user = request.user
        else:
            _thread_locals.user = None
            
        response = self.get_response(request)
        
        # Limpiar al terminar
        _thread_locals.user = None
        return response
