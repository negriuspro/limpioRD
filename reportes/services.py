# reportes/services.py
from django.db import transaction
from django.utils import timezone
from .models import Reporte, HistorialEstadoReporte
from .tasks import notificar_ciudadano_cambio_estado

from core.utils import registrar_auditoria

class ReporteService:
    @staticmethod
    @transaction.atomic
    def crear_reporte(datos, usuario):
        """Crea un reporte y registra auditoría."""
        reporte = Reporte(
            ciudadano=usuario,
            municipio_id=datos['municipio_id'],
            categoria_id=datos['categoria_id'],
            latitud=datos['latitud'],
            longitud=datos['longitud'],
            descripcion=datos.get('descripcion', ''),
            barrio=datos.get('barrio', ''),
            referencia=datos.get('referencia', ''),
            foto=datos.get('foto'),
        )
        reporte.urgencia = reporte.calcular_urgencia_automatica()
        reporte.save()

        # Auditoría
        registrar_auditoria(usuario, reporte, 'crear', detalles={'categoria': reporte.categoria.nombre})

        # Los puntos se otorgan solo cuando el reporte se marca como RESUELTO
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
            delta = reporte.resuelto_en - reporte.creado_en
            reporte.tiempo_respuesta_horas = delta.total_seconds() / 3600

        reporte.save()

        # Otorgar puntos al ciudadano solo al resolver (y solo si tiene ciudadano asignado)
        if nuevo_estado == Reporte.ESTADO_RESUELTO and estado_anterior != Reporte.ESTADO_RESUELTO:
            if reporte.ciudadano:
                from gamificacion.services import PuntosService
                puntos = PuntosService.otorgar_puntos(reporte.ciudadano, 'reporte_resuelto', reporte=reporte)
                reporte.puntos_otorgados = puntos
                reporte.save(update_fields=['puntos_otorgados'])

        # Registro de historial de estado (ya existía)
        HistorialEstadoReporte.objects.create(
            reporte=reporte,
            estado_anterior=estado_anterior,
            estado_nuevo=nuevo_estado,
            cambiado_por=usuario_admin,
            notas=notas
        )

        # Auditoría global extendida
        registrar_auditoria(usuario_admin, reporte, 'editar', detalles={'nuevo_estado': nuevo_estado, 'notas': notas})

        # Notificar (si Celery/broker no está disponible, ejecutar directo)
        try:
            notificar_ciudadano_cambio_estado.delay(reporte.id, estado_anterior, nuevo_estado)
        except Exception:
            notificar_ciudadano_cambio_estado(reporte.id, estado_anterior, nuevo_estado)

        return reporte
