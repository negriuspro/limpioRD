# accounts/views.py
import re

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages

from django.contrib.auth.decorators import login_required
from gamificacion.services import PuntosService
from ayuntamientos.models import Municipio
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

    municipios = Municipio.objects.filter(esta_activo=True).order_by('nombre')

    if request.method == 'POST':
        nombre       = request.POST.get('nombre',       '').strip()
        apellido     = request.POST.get('apellido',     '').strip()
        email        = request.POST.get('email',        '').strip().lower()
        telefono     = request.POST.get('telefono',     '').strip()
        cedula       = request.POST.get('cedula',       '').strip()
        edad_raw     = request.POST.get('edad',         '').strip()
        municipio_id = request.POST.get('municipio',   '').strip()
        password     = request.POST.get('password',    '')

        # Validaciones
        errors = []
        if not nombre:
            errors.append('El nombre es requerido.')
        if not apellido:
            errors.append('El apellido es requerido.')
        if not email:
            errors.append('El correo electrónico es requerido.')
        elif not _is_valid_email(email):
            errors.append('El correo electrónico no tiene un formato válido.')
        if not telefono:
            errors.append('El teléfono es requerido.')
        if not cedula:
            errors.append('La cédula es requerida.')
        if not edad_raw:
            errors.append('La edad es requerida.')
        if not municipio_id:
            errors.append('El municipio es requerido.')
        if not password:
            errors.append('La contraseña es requerida.')
        elif not _is_strong_password(password):
            errors.append('La contraseña debe tener al menos 8 caracteres.')

        edad = None
        if edad_raw:
            try:
                edad = int(edad_raw)
                if edad < 14 or edad > 120:
                    errors.append('La edad debe estar entre 14 y 120 años.')
            except ValueError:
                errors.append('La edad debe ser un número válido.')

        municipio_obj = None
        if municipio_id:
            try:
                municipio_obj = Municipio.objects.get(id=municipio_id, esta_activo=True)
            except Municipio.DoesNotExist:
                errors.append('El municipio seleccionado no es válido.')

        if errors:
            for err in errors:
                messages.error(request, err)
            return render(request, 'accounts/signup.html', {'post': request.POST, 'municipios': municipios})

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado. ¿Olvidaste tu contraseña?')
            return render(request, 'accounts/signup.html', {'post': request.POST, 'municipios': municipios})

        if cedula and Usuario.objects.filter(cedula=cedula).exclude(cedula='').exists():
            messages.error(request, 'Esta cédula ya está registrada.')
            return render(request, 'accounts/signup.html', {'post': request.POST, 'municipios': municipios})

        try:
            user = Usuario.objects.create_user(
                email=email,
                password=password,
                nombre=nombre,
                apellido=apellido,
                telefono=telefono,
                cedula=cedula,
                edad=edad,
                municipio=municipio_obj,
                rol=Usuario.ROL_CIUDADANO,
            )
            PuntosService.otorgar_puntos(user, 'registro_nuevo')
            login(request, user)
            messages.success(request, f'¡Bienvenido a LimpioRD, {nombre}! Tu cuenta fue creada exitosamente.')
            return redirect('/ciudadano/dashboard/')
        except Exception as e:
            messages.error(request, 'Ocurrió un error al crear tu cuenta. Por favor intenta de nuevo.')

    return render(request, 'accounts/signup.html', {'municipios': municipios})


# ── Perfil ──────────────────────────────────────────────────────────────────
@login_required
def perfil_view(request):
    municipios = Municipio.objects.filter(esta_activo=True).order_by('nombre')

    if request.method == 'POST':
        nombre       = request.POST.get('nombre',    '').strip()
        apellido     = request.POST.get('apellido',  '').strip()
        telefono     = request.POST.get('telefono',  '').strip()
        barrio       = request.POST.get('barrio',    '').strip()
        municipio_id = request.POST.get('municipio', '').strip()

        errors = []
        if not nombre:
            errors.append('El nombre es requerido.')
        if not apellido:
            errors.append('El apellido es requerido.')

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, 'accounts/perfil.html', {'municipios': municipios})

        user = request.user
        user.nombre   = nombre
        user.apellido = apellido
        user.telefono = telefono
        user.barrio   = barrio
        if municipio_id:
            try:
                user.municipio = Municipio.objects.get(id=municipio_id, esta_activo=True)
            except Municipio.DoesNotExist:
                pass
        user.save(update_fields=['nombre', 'apellido', 'telefono', 'barrio', 'municipio'])
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('accounts:perfil')

    return render(request, 'accounts/perfil.html', {'municipios': municipios})


# ── Logout ──────────────────────────────────────────────────────────────────
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.info(request, 'Sesión cerrada exitosamente.')
    return redirect('/')
