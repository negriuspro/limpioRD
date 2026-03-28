# accounts/views.py
import re

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from gamificacion.services import PuntosService
from .models import Usuario


# ── Helpers ────────────────────────────────────────────────────────────────
def _is_valid_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def _is_strong_password(password: str) -> bool:
    """Mínimo 8 caracteres."""
    return len(password) >= 8


def _redirect_after_login(user):
    """Redirige según el rol del usuario."""
    if user.rol in [Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA]:
        return redirect('/panel/dashboard/')
    return redirect('/ciudadano/dashboard/')


# ── Login ───────────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return _redirect_after_login(request.user)

    if request.method == 'POST':
        email    = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        if not email or not password:
            messages.error(request, 'Por favor ingresa tu correo y contraseña.')
            return render(request, 'accounts/login.html')

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido de nuevo, {user.nombre}!')
            return _redirect_after_login(user)
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')

    return render(request, 'accounts/login.html')


# ── Signup ──────────────────────────────────────────────────────────────────
def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')

    if request.method == 'POST':
        nombre   = request.POST.get('nombre',   '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email    = request.POST.get('email',    '').strip().lower()
        password = request.POST.get('password', '')

        # Validaciones
        errors = []
        if not nombre:
            errors.append('El nombre es requerido.')
        if not email:
            errors.append('El correo electrónico es requerido.')
        elif not _is_valid_email(email):
            errors.append('El correo electrónico no tiene un formato válido.')
        if not password:
            errors.append('La contraseña es requerida.')
        elif not _is_strong_password(password):
            errors.append('La contraseña debe tener al menos 8 caracteres.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/signup.html', {'post': request.POST})

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado. ¿Olvidaste tu contraseña?')
            return render(request, 'accounts/signup.html', {'post': request.POST})

        try:
            user = Usuario.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                apellido=apellido,
                rol=Usuario.ROL_CIUDADANO,
            )
            PuntosService.otorgar_puntos(user, 'registro_nuevo')
            login(request, user)
            messages.success(request, f'¡Bienvenido a LimpioRD, {nombre}! Tu cuenta fue creada exitosamente.')
            return redirect('/ciudadano/dashboard/')
        except Exception as e:
            messages.error(request, 'Ocurrió un error al crear tu cuenta. Por favor intenta de nuevo.')

    return render(request, 'accounts/signup.html')


# ── Logout ──────────────────────────────────────────────────────────────────
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Sesión cerrada exitosamente.')
    return redirect('/')
