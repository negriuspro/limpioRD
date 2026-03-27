# reportes/services.py
from django.db import transaction
from django.utils import timezone
from .models import Reporte, HistorialEstadoReporte
from .tasks import notificar_ciudadano_cambio_estado

class ReporteService:
    @staticmethod
    @transaction.atomic
    def crear_reporte(datos, usuario):
        """Crea un reporte y verifica si es una zona crítica existente."""
        reporte = Reporte(
            ciudadano=usuario,
            municipio_id=datos['municipio_id'],
            categoria_id=datos['categoria_id'],
            latitud=datos['latitud'],
            longitud=datos['longitud'],
            descripcion=datos.get('descripcion', ''),
            foto=datos.get('foto'),
        )
        reporte.urgencia = reporte.calcular_urgencia_automatica()
        reporte.save()

        # Otorgar puntos iniciales (ej: 10 puntos por reportar)
        from gamificacion.services import PuntosService
        PuntosService.otorgar_puntos(usuario, 'reporte_nuevo', reporte=reporte)

        return reporte

    @staticmethod
    @transaction.atomic
    def cambiar_estado(reporte_id, nuevo_estado, usuario_admin, notas=""):
        reporte = Reporte.objects.select_for_update().get(id=reporte_id)
        estado_anterior = reporte.estado

        if estado_anterior == nuevo_estado:
            return reporte

        reporte.estado = nuevo_estado
        
        if nuevo_estado == Reporte.ESTADO_RESUELTO:
            reporte.resuelto_en = timezone.now()
            # Calcular tiempo de respuesta
            delta = reporte.resuelto_en - reporte.creado_en
            reporte.tiempo_respuesta_horas = delta.total_seconds() / 3600
        
        reporte.save()

        HistorialEstadoReporte.objects.create(
            reporte=reporte,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            cambiado_por=usuario_admin,
            notas=notas
        )

        # Disparar tarea asíncrona (Celery)
        notificar_ciudadano_cambio_estado.delay(reporte.id, estado_anterior, nuevo_estado)

        return reporte
