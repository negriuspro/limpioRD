# reportes/views.py  — Módulo Ciudadano
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from ayuntamientos.models import Municipio
from gamificacion.models import PerfilGamificacion, TransaccionPuntos
from gamificacion.services import PuntosService
from .models import Reporte, CategoriaResiduo
from .services import ReporteService


# ── Dashboard Ciudadano ─────────────────────────────────────────────────────
@login_required
def dashboard_ciudadano(request):
    user = request.user
    # Redirigir funcionarios/admins al panel municipal
    if user.rol in ['funcionario_municipal', 'admin_ayuntamiento', 'admin_sistema']:
        return redirect('/panel/dashboard/')

    mis_reportes = Reporte.objects.filter(ciudadano=user).order_by('-creado_en')[:5]

    # Perfil de gamificación (crear si no existe)
    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=user)
    ultimas_transacciones = perfil.transacciones.all()[:5]

    stats = {
        'total': Reporte.objects.filter(ciudadano=user).count(),
        'resueltos': Reporte.objects.filter(ciudadano=user, estado=Reporte.ESTADO_RESUELTO).count(),
        'pendientes': Reporte.objects.filter(ciudadano=user, estado=Reporte.ESTADO_PENDIENTE).count(),
        'puntos': perfil.puntos_disponibles,
    }

    return render(request, 'ciudadano/dashboard.html', {
        'mis_reportes': mis_reportes,
        'perfil': perfil,
        'stats': stats,
        'ultimas_transacciones': ultimas_transacciones,
    })


# ── Crear Reporte ──────────────────────────────────────────────────────────
@login_required
def crear_reporte(request):
    categorias = CategoriaResiduo.objects.filter(activo=True)
    municipios = Municipio.objects.all()

    if request.method == 'POST':
        municipio_id = request.POST.get('municipio')
        categoria_id = request.POST.get('categoria')
        descripcion  = request.POST.get('description', '').strip()
        barrio       = request.POST.get('barrio', '').strip()
        referencia   = request.POST.get('referencia', '').strip()
        latitud      = request.POST.get('latitud', '').strip()
        longitud     = request.POST.get('longitud', '').strip()

        # Validación básica
        if not municipio_id or not categoria_id or not descripcion:
            messages.error(request, 'Por favor completa los campos requeridos.')
            return render(request, 'ciudadano/crear_reporte.html', {
                'categorias': categorias, 'municipios': municipios,
                'post': request.POST,
            })

        # Si no hay coordenadas, usar centro del municipio
        if not latitud or not longitud:
            try:
                mun = Municipio.objects.get(id=municipio_id)
                latitud  = str(mun.latitud_centro)
                longitud = str(mun.longitud_centro)
            except Municipio.DoesNotExist:
                latitud, longitud = '18.4861', '-69.9312'

        datos = {
            'municipio_id': municipio_id,
            'categoria_id': categoria_id,
            'descripcion':  descripcion,
            'barrio':       barrio,
            'referencia':   referencia,
            'latitud':      latitud,
            'longitud':     longitud,
        }
        try:
            reporte = ReporteService.crear_reporte(datos, request.user)
            messages.success(request, f'¡Reporte enviado exitosamente! Ganaste 10 puntos LimpioRD 🌿')
            return redirect('/ciudadano/mis-reportes/')
        except Exception as e:
            messages.error(request, f'Error al enviar el reporte: {str(e)}')

    return render(request, 'ciudadano/crear_reporte.html', {
        'categorias': categorias,
        'municipios': municipios,
    })


# ── Mis Reportes ────────────────────────────────────────────────────────────
from django.core.paginator import Paginator

@login_required
def mis_reportes(request):
    estado = request.GET.get('estado', '')
    qs = Reporte.objects.filter(ciudadano=request.user).select_related('categoria', 'municipio')
    if estado:
        qs = qs.filter(estado=estado)
    qs = qs.order_by('-creado_en')

    paginator = Paginator(qs, 10) # 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'ciudadano/mis_reportes.html', {
        'reportes': page_obj,
        'estados': Reporte.ESTADOS,
        'estado_sel': estado,
    })


# ── Detalle Reporte ─────────────────────────────────────────────────────────
@login_required
def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id, ciudadano=request.user)
    historial = reporte.historial.all()
    return render(request, 'ciudadano/detalle_reporte.html', {
        'reporte': reporte,
        'historial': historial,
    })


# ── Mis Puntos ──────────────────────────────────────────────────────────────
@login_required
def mis_puntos(request):
    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=request.user)
    transacciones = perfil.transacciones.all()[:20]
    return render(request, 'ciudadano/mis_puntos.html', {
        'perfil': perfil,
        'transacciones': transacciones,
    })
