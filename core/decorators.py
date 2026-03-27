# core/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def rol_requerido(roles_permitidos):
    """Decorador PBAC — redirige al login si no está autenticado o no tiene el rol correcto."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('/accounts/login/')
            if request.user.rol not in roles_permitidos:
                messages.error(request, 'No tienes permisos para acceder a esta sección.')
                return redirect('/')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
