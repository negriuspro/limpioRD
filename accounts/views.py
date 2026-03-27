# accounts/views.py (updated with registration)
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Usuario

def login_view(request):
    if request.user.is_authenticated:
        if request.user.rol in [Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA]:
            return redirect('/panel/dashboard/')
        return redirect('/ciudadano/dashboard/')
    
    if request.method == 'POST':
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'¡Bienvenido, {user.nombre}!')
            if user.rol in [Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA]:
                return redirect('/panel/dashboard/')
            return redirect('/ciudadano/dashboard/')
        else:
            messages.error(request, 'Credenciales incorrectas.')
    
    return render(request, 'accounts/login.html')

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('/')
        
    if request.method == 'POST':
        nombre   = request.POST.get('nombre', '').strip()
        apellido = request.POST.get('apellido', '').strip()
        email    = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if not nombre or not email or not password:
            messages.error(request, 'Completa todos los campos obligatorios.')
            return render(request, 'accounts/signup.html')
            
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Este correo ya está registrado.')
            return render(request, 'accounts/signup.html')
            
        user = Usuario.objects.create_user(
            email=email, password=password,
            nombre=nombre, apellido=apellido,
            rol=Usuario.ROL_CIUDADANO
        )
        # Otorgar puntos por registro
        from gamificacion.services import PuntosService
        PuntosService.otorgar_puntos(user, 'registro_nuevo')
        
        login(request, user)
        messages.success(request, '¡Cuenta creada con éxito! Bienvenido a LimpioRD.')
        return redirect('/ciudadano/dashboard/')
        
    return render(request, 'accounts/signup.html')

def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('/')
