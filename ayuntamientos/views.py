# ayuntamientos/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from core.decorators import rol_requerido
from accounts.models import Usuario
from reportes.models import Reporte

@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def dashboard(request):
    municipio = getattr(request.user, 'municipio', None)
    qs = Reporte.objects.all()
    if municipio:
        qs = qs.filter(municipio=municipio)

    hoy = timezone.now()
    hace_7_dias = hoy - timedelta(days=7)

    total      = qs.count()
    pendientes = qs.filter(estado=Reporte.ESTADO_PENDIENTE).count()
    resueltos  = qs.filter(estado=Reporte.ESTADO_RESUELTO).count()
    en_proceso = qs.filter(estado=Reporte.ESTADO_EN_PROCESO).count()

    # Tiempo de respuesta promedio en horas
    promedio = qs.filter(tiempo_respuesta_horas__isnull=False).aggregate(
        avg=Avg('tiempo_respuesta_horas')
    )['avg'] or 0

    # Reportes últimos 7 días para gráfico
    reportes_semana = []
    labels_semana   = []
    for i in range(6, -1, -1):
        dia = hoy - timedelta(days=i)
        count = qs.filter(creado_en__date=dia.date()).count()
        reportes_semana.append(count)
        labels_semana.append(dia.strftime('%a'))

    # Últimos 8 reportes
    ultimos = qs.select_related('ciudadano', 'categoria', 'municipio').order_by('-creado_en')[:8]

    # Por estado (para chart de dona)
    por_estado = {
        'Pendiente': pendientes,
        'En Proceso': en_proceso,
        'Resuelto':   resueltos,
        'Rechazado':  qs.filter(estado=Reporte.ESTADO_RECHAZADO).count(),
    }

    return render(request, 'ayuntamientos/dashboard.html', {
        'total': total,
        'pendientes': pendientes,
        'resueltos': resueltos,
        'en_proceso': en_proceso,
        'promedio_horas': round(promedio, 1),
        'ultimos': ultimos,
        'reportes_semana': reportes_semana,
        'labels_semana': labels_semana,
        'por_estado': por_estado,
    })


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def mapa_calor(request):
    municipio = getattr(request.user, 'municipio', None)
    qs = Reporte.objects.all()
    if municipio:
        qs = qs.filter(municipio=municipio)

    # Solo reportes activos con coordenadas para el mapa
    puntos = list(qs.exclude(
        estado=Reporte.ESTADO_RESUELTO
    ).values('id', 'latitud', 'longitud', 'descripcion', 'urgencia', 'estado', 'barrio'))

    # Serializar IDs a string (son UUID)
    for p in puntos:
        p['id'] = str(p['id'])
        p['latitud'] = float(p['latitud'])
        p['longitud'] = float(p['longitud'])

    import json
    return render(request, 'ayuntamientos/mapa.html', {
        'puntos_json': json.dumps(puntos),
        'total_activos': len(puntos),
    })


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def lista_reportes(request):
    municipio = getattr(request.user, 'municipio', None)
    qs = Reporte.objects.select_related('ciudadano', 'categoria', 'municipio').all()
    if municipio:
        qs = qs.filter(municipio=municipio)

    estado = request.GET.get('estado', '')
    if estado:
        qs = qs.filter(estado=estado)

    q = request.GET.get('q', '')
    if q:
        qs = qs.filter(Q(barrio__icontains=q) | Q(descripcion__icontains=q) | Q(direccion__icontains=q))

    qs = qs.order_by('-creado_en')
    estados = Reporte.ESTADOS

    return render(request, 'ayuntamientos/reportes_lista.html', {
        'reportes': qs[:50],
        'estados': estados,
        'estado_sel': estado,
        'q': q,
    })


@login_required
@rol_requerido([Usuario.ROL_FUNCIONARIO, Usuario.ROL_ADMIN_AYUNTAMIENTO, Usuario.ROL_ADMIN_SISTEMA])
def cambiar_estado_reporte(request, reporte_id):
    if request.method == 'POST':
        from reportes.services import ReporteService
        nuevo_estado = request.POST.get('estado')
        notas = request.POST.get('notas', '')
        ReporteService.cambiar_estado(reporte_id, nuevo_estado, request.user, notas)
        from django.contrib import messages
        messages.success(request, f'Estado actualizado a "{nuevo_estado}" correctamente.')
    return redirect('/panel/reportes/')
