# reportes/views.py  — Módulo Ciudadano
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone

from ayuntamientos.models import Municipio
from gamificacion.models import PerfilGamificacion
from gamificacion.services import PuntosService

from django.http import JsonResponse
from .models import Reporte, CategoriaResiduo
from .services import ReporteService


# ── Dashboard Ciudadano ────────────────────────────────────────────────────
@login_required
def dashboard_ciudadano(request):
    user = request.user
    # Redirigir funcionarios/admins al panel municipal
    if user.rol in ['funcionario_municipal', 'admin_ayuntamiento', 'admin_sistema']:
        return redirect('/panel/dashboard/')

    mis_reportes = Reporte.objects.filter(ciudadano=user).select_related(
        'categoria', 'municipio'
    ).order_by('-creado_en')[:5]

    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=user)

    stats = {
        'total':     Reporte.objects.filter(ciudadano=user).count(),
        'resueltos': Reporte.objects.filter(ciudadano=user, estado=Reporte.ESTADO_RESUELTO).count(),
        'pendientes': Reporte.objects.filter(ciudadano=user, estado=Reporte.ESTADO_PENDIENTE).count(),
        'en_proceso': Reporte.objects.filter(ciudadano=user, estado=Reporte.ESTADO_EN_PROCESO).count(),
        'puntos':    perfil.puntos_disponibles,
    }

    return render(request, 'ciudadano/dashboard.html', {
        'mis_reportes': mis_reportes,
        'perfil':       perfil,
        'stats':        stats,
    })


# ── Crear Reporte ──────────────────────────────────────────────────────────
@login_required
def crear_reporte(request):
    categorias = CategoriaResiduo.objects.filter(activo=True)
    municipios = Municipio.objects.all()

    if request.method == 'POST':
        municipio_id = request.POST.get('municipio', '').strip()
        categoria_id = request.POST.get('categoria', '').strip()
        descripcion  = request.POST.get('descripcion', '').strip()
        barrio       = request.POST.get('barrio', '').strip()
        referencia   = request.POST.get('referencia', '').strip()
        latitud      = request.POST.get('latitud', '').strip()
        longitud     = request.POST.get('longitud', '').strip()
        foto         = request.FILES.get('foto')  # Manejo de archivo de foto

        # Validación
        if not municipio_id or not categoria_id or not descripcion:
            messages.error(request, 'Por favor completa los campos requeridos: municipio, categoría y descripción.')
            return render(request, 'ciudadano/crear_reporte.html', {
                'categorias': categorias,
                'municipios': municipios,
                'post':       request.POST,
            })

        # Fallback coordenadas si no se proporcionaron
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
            'foto':         foto,
        }
        try:
            ReporteService.crear_reporte(datos, request.user)
            messages.success(request, '¡Reporte enviado! Recibirás puntos cuando sea resuelto.')
            return redirect('/ciudadano/mis-reportes/')
        except Exception as e:
            messages.error(request, f'Error al enviar el reporte: {str(e)}')

    return render(request, 'ciudadano/crear_reporte.html', {
        'categorias':      categorias,
        'municipios':      municipios,
        'user_municipio':  request.user.municipio,
    })


# ── Mis Reportes ─────────────────────────────────────────────────────────
@login_required
def mis_reportes(request):
    estado = request.GET.get('estado', '')
    buscar = request.GET.get('q', '')

    qs = Reporte.objects.filter(ciudadano=request.user).select_related('categoria', 'municipio')
    if estado:
        qs = qs.filter(estado=estado)
    if buscar:
        qs = qs.filter(barrio__icontains=buscar) | qs.filter(descripcion__icontains=buscar)

    qs = qs.order_by('-creado_en')

    paginator  = Paginator(qs, 9)
    page_number = request.GET.get('page')
    page_obj   = paginator.get_page(page_number)

    return render(request, 'ciudadano/mis_reportes.html', {
        'reportes':   page_obj,
        'estados':    Reporte.ESTADOS,
        'estado_sel': estado,
        'buscar':     buscar,
    })


# ── Detalle Reporte ────────────────────────────────────────────────────────
@login_required
def detalle_reporte(request, reporte_id):
    reporte  = get_object_or_404(Reporte, id=reporte_id, ciudadano=request.user)
    historial = reporte.historial.select_related('cambiado_por').all()
    return render(request, 'ciudadano/detalle_reporte.html', {
        'reporte':  reporte,
        'historial': historial,
    })


# ── Confirmar Reporte (votos ciudadanos) ──────────────────────────────────
@login_required
def confirmar_reporte(request, reporte_id):
    if request.method != 'POST':
        return JsonResponse({'ok': False}, status=405)
    reporte = get_object_or_404(Reporte, id=reporte_id)
    reporte.votos_confirmacion = (reporte.votos_confirmacion or 0) + 1
    reporte.save(update_fields=['votos_confirmacion'])
    return JsonResponse({'ok': True, 'votos': reporte.votos_confirmacion})


# ── Mis Puntos ─────────────────────────────────────────────────────────────
@login_required
def mis_puntos(request):
    from comercios.models import Recompensa
    from accounts.models import Usuario

    perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=request.user)
    transacciones = perfil.transacciones.all()[:30]

    disponibles = perfil.puntos_disponibles
    recompensas_qs = Recompensa.objects.filter(activo=True).select_related('comercio').order_by('puntos_requeridos')
    recompensas = []
    for r in recompensas_qs:
        recompensas.append({
            'obj':    r,
            'faltan': max(0, r.puntos_requeridos - disponibles),
            'puede':  disponibles >= r.puntos_requeridos,
        })

    top_ciudadanos = (
        PerfilGamificacion.objects
        .select_related('usuario')
        .order_by('-puntos_totales')[:5]
    )
    total_ciudadanos = Usuario.objects.filter(rol='ciudadano', esta_activo=True).count()

    return render(request, 'ciudadano/mis_puntos.html', {
        'perfil':           perfil,
        'transacciones':    transacciones,
        'recompensas':      recompensas,
        'top_ciudadanos':   top_ciudadanos,
        'total_ciudadanos': total_ciudadanos,
    })
