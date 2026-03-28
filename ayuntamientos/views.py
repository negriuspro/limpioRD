# ayuntamientos/views.py
import json

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta

from core.decorators import rol_requerido
from accounts.models import Usuario
from reportes.models import Reporte


def _get_queryset_para_municipio(user):
    """Filtra reportes según el municipio del usuario autenticado."""
    qs = Reporte.objects.all()
    municipio = getattr(user, 'municipio', None)
    if municipio:
        qs = qs.filter(municipio=municipio)
    return qs


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def dashboard(request):
    qs = _get_queryset_para_municipio(request.user)

    hoy = timezone.now()

    total      = qs.count()
    pendientes = qs.filter(estado=Reporte.ESTADO_PENDIENTE).count()
    resueltos  = qs.filter(estado=Reporte.ESTADO_RESUELTO).count()
    en_proceso = qs.filter(estado=Reporte.ESTADO_EN_PROCESO).count()
    rechazados = qs.filter(estado=Reporte.ESTADO_RECHAZADO).count()

    # Tiempo de respuesta promedio
    promedio = qs.filter(tiempo_respuesta_horas__isnull=False).aggregate(
        avg=Avg('tiempo_respuesta_horas')
    )['avg'] or 0

    # Últimos 7 días para gráfico
    reportes_semana = []
    labels_semana   = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        count = qs.filter(creado_en__date=dia.date()).count()
        reportes_semana.append(count)
        labels_semana.append(dia.strftime('%a'))

    ultimos = qs.select_related('ciudadano', 'categoria', 'municipio').order_by('-creado_en')[:8]

    return render(request, 'ayuntamientos/dashboard.html', {
        'total':          total,
        'pendientes':     pendientes,
        'resueltos':      resueltos,
        'en_proceso':     en_proceso,
        'rechazados':     rechazados,
        'promedio_horas': round(promedio, 1),
        'ultimos':        ultimos,
        'reportes_semana': json.dumps(reportes_semana),
        'labels_semana':   json.dumps(labels_semana),
    })


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def mapa_calor(request):
    qs = _get_queryset_para_municipio(request.user)

    # Incluir categoría para iconos diferenciados en el mapa
    puntos_qs = (
        qs.exclude(estado=Reporte.ESTADO_RESUELTO)
          .select_related('categoria')
          .values(
              'id', 'latitud', 'longitud', 'descripcion',
              'urgencia', 'estado', 'barrio', 'foto',
              'categoria__nombre', 'categoria__color', 'categoria__icono',
          )
    )

    from django.conf import settings
    media_url = settings.MEDIA_URL

    puntos = []
    for p in puntos_qs:
        foto_path = p.get('foto') or ''
        foto_url = (media_url + foto_path) if foto_path else ''
        puntos.append({
            'id':         str(p['id']),
            'latitud':    str(p['latitud']),
            'longitud':   str(p['longitud']),
            'descripcion': p['descripcion'] or '',
            'urgencia':   p['urgencia'],
            'estado':     p['estado'],
            'barrio':     p['barrio'] or '',
            'categoria':  p['categoria__nombre'] or 'General',
            'color':      p['categoria__color'] or '#6b7280',
            'icono':      p['categoria__icono'] or 'trash',
            'foto_url':   foto_url,
        })

    return render(request, 'ayuntamientos/mapa.html', {
        'puntos_json':  json.dumps(puntos),
        'total_activos': len(puntos),
    })


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def lista_reportes(request):
    qs = _get_queryset_para_municipio(request.user).select_related(
        'ciudadano', 'categoria', 'municipio'
    )

    estado = request.GET.get('estado', '')
    if estado:
        qs = qs.filter(estado=estado)

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(
            Q(barrio__icontains=q) |
            Q(descripcion__icontains=q) |
            Q(direccion__icontains=q)
        )

    qs = qs.order_by('-creado_en')

    return render(request, 'ayuntamientos/reportes_lista.html', {
        'reportes':   qs[:50],
        'estados':    Reporte.ESTADOS,
        'estado_sel': estado,
        'q':          q,
    })


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def api_puntos_mapa(request):
    """JSON con reportes activos para polling del mapa."""
    qs = _get_queryset_para_municipio(request.user)
    puntos_qs = (
        qs.exclude(estado=Reporte.ESTADO_RESUELTO)
          .select_related('categoria')
          .values('id', 'latitud', 'longitud', 'descripcion',
                  'urgencia', 'estado', 'barrio', 'foto',
                  'categoria__nombre', 'categoria__color', 'categoria__icono')
    )
    from django.conf import settings
    media_url = settings.MEDIA_URL
    puntos = []
    for p in puntos_qs:
        foto_path = p.get('foto') or ''
        puntos.append({
            'id':         str(p['id']),
            'latitud':    str(p['latitud']),
            'longitud':   str(p['longitud']),
            'descripcion': p['descripcion'] or '',
            'urgencia':   p['urgencia'],
            'estado':     p['estado'],
            'barrio':     p['barrio'] or '',
            'categoria':  p['categoria__nombre'] or 'General',
            'color':      p['categoria__color'] or '#6b7280',
            'icono':      p['categoria__icono'] or 'trash',
            'foto_url':   (media_url + foto_path) if foto_path else '',
        })
    return JsonResponse({'puntos': puntos, 'total': len(puntos)})


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def api_stats_dashboard(request):
    """JSON con KPIs para polling del dashboard."""
    qs   = _get_queryset_para_municipio(request.user)
    hoy  = timezone.now()
    reportes_semana = []
    labels_semana   = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        reportes_semana.append(qs.filter(creado_en__date=dia.date()).count())
        labels_semana.append(dia.strftime('%a'))
    promedio = qs.filter(tiempo_respuesta_horas__isnull=False).aggregate(
        avg=Avg('tiempo_respuesta_horas'))['avg'] or 0
    return JsonResponse({
        'total':           qs.count(),
        'pendientes':      qs.filter(estado=Reporte.ESTADO_PENDIENTE).count(),
        'resueltos':       qs.filter(estado=Reporte.ESTADO_RESUELTO).count(),
        'en_proceso':      qs.filter(estado=Reporte.ESTADO_EN_PROCESO).count(),
        'rechazados':      qs.filter(estado=Reporte.ESTADO_RECHAZADO).count(),
        'promedio_horas':  round(promedio, 1),
        'reportes_semana': reportes_semana,
        'labels_semana':   labels_semana,
    })


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def cambiar_estado_reporte(request, reporte_id):
    if request.method == 'POST':
        from django.http import JsonResponse
        from reportes.services import ReporteService
        nuevo_estado = request.POST.get('estado')
        notas        = request.POST.get('notas', '')
        ReporteService.cambiar_estado(reporte_id, nuevo_estado, request.user, notas)
        # Si es petición AJAX (desde el mapa) responde JSON; si es form normal redirige
        if request.headers.get('X-CSRFToken'):
            return JsonResponse({'ok': True})
        messages.success(request, 'Estado actualizado correctamente.')
    return redirect('/panel/reportes/')
