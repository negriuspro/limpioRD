# analytics/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from ayuntamientos.models import Municipio
from reportes.models import Reporte
from .models import EstadisticaDiaria

@shared_task
def generar_estadisticas_diarias():
    """Ejecutado a la medianoche (vía Celery Beat)."""
    ayer = timezone.now().date() - timedelta(days=1)
    
    for municipio in Municipio.objects.filter(esta_activo=True):
        reportes_ayer = Reporte.objects.filter(municipio=municipio, creado_en__date=ayer)
        
        total = reportes_ayer.count()
        resueltos = reportes_ayer.filter(estado=Reporte.ESTADO_RESUELTO).count()
        pendientes = reportes_ayer.filter(estado__in=[Reporte.ESTADO_PENDIENTE, Reporte.ESTADO_REVISANDO]).count()
        
        # Crear snapshot
        EstadisticaDiaria.objects.update_or_create(
            municipio=municipio,
            fecha=ayer,
            defaults={
                'total_reportes': total,
                'reportes_resueltos': resueltos,
                'reportes_pendientes': pendientes,
                # Cálculos adicionales requeridos (tiempo_respuesta_promedio, usuarios)...
            }
        )
    return "Estadísticas generadas correctamente"
