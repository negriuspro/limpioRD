# reportes/models.py

from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class CategoriaResiduo(TimeStampedModel):
    """Tipo de residuo reportado."""
    nombre   = models.CharField(max_length=80)
    icono    = models.CharField(max_length=50, default='trash')  # Nombre de ícono Heroicons
    color    = models.CharField(max_length=7, default='#6B7280')  # Hex color para el mapa
    activo   = models.BooleanField(default=True)

    class Meta:
        db_table = 'categorias_residuos'


class Reporte(TimeStampedModel):
    """
    Reporte ciudadano de acumulación de basura.
    Es el modelo central de toda la plataforma.
    """
    ESTADO_PENDIENTE    = 'pendiente'
    ESTADO_REVISANDO    = 'revisando'
    ESTADO_EN_PROCESO   = 'en_proceso'
    ESTADO_RESUELTO     = 'resuelto'
    ESTADO_RECHAZADO    = 'rechazado'   # Spam o duplicado

    ESTADOS = [
        (ESTADO_PENDIENTE,  'Pendiente de revisión'),
        (ESTADO_REVISANDO,  'En revisión por el ayuntamiento'),
        (ESTADO_EN_PROCESO, 'Camión en camino'),
        (ESTADO_RESUELTO,   'Resuelto'),
        (ESTADO_RECHAZADO,  'Rechazado'),
    ]

    URGENCIA_BAJA    = 1
    URGENCIA_MEDIA   = 2
    URGENCIA_ALTA    = 3
    URGENCIA_CRITICA = 4

    URGENCIAS = [
        (URGENCIA_BAJA,    'Baja'),
        (URGENCIA_MEDIA,   'Media'),
        (URGENCIA_ALTA,    'Alta'),
        (URGENCIA_CRITICA, 'Crítica'),
    ]

    # Relaciones
    ciudadano    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, related_name='reportes')
    municipio    = models.ForeignKey('ayuntamientos.Municipio', on_delete=models.CASCADE,
                                     related_name='reportes')
    categoria    = models.ForeignKey(CategoriaResiduo, on_delete=models.SET_NULL,
                                     null=True, related_name='reportes')
    zona_critica = models.ForeignKey('ayuntamientos.ZonaCritica', on_delete=models.SET_NULL,
                                     null=True, blank=True)
    asignado_a   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='reportes_asignados')

    # Ubicación geográfica
    latitud       = models.DecimalField(max_digits=9, decimal_places=6)
    longitud      = models.DecimalField(max_digits=9, decimal_places=6)
    direccion     = models.CharField(max_length=300, blank=True)
    barrio        = models.CharField(max_length=100, blank=True)
    referencia    = models.CharField(max_length=200, blank=True,
                                      help_text='Ej: Frente al colmado La Fe')

    # Contenido
    descripcion  = models.TextField(blank=True)
    foto         = models.ImageField(upload_to='reportes/%Y/%m/', blank=True, null=True)
    foto_url     = models.URLField(blank=True)  # URL firmada de S3 (caché)

    # Estado y prioridad
    estado       = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE,
                                     db_index=True)
    urgencia     = models.IntegerField(choices=URGENCIAS, default=URGENCIA_MEDIA)
    es_anonimo   = models.BooleanField(default=False)
    votos_confirmacion = models.IntegerField(default=0)  # Otros usuarios confirman el problema

    # Resolución
    resuelto_en     = models.DateTimeField(null=True, blank=True)
    tiempo_respuesta_horas = models.DecimalField(max_digits=6, decimal_places=2,
                                                  null=True, blank=True)
    nota_resolucion = models.TextField(blank=True)
    foto_resolucion = models.ImageField(upload_to='resoluciones/%Y/%m/', blank=True, null=True)

    # Puntos otorgados al ciudadano
    puntos_otorgados = models.IntegerField(default=0)

    class Meta:
        db_table = 'reportes'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'
        ordering = ['-creado_en']
        indexes = [
            models.Index(fields=['estado', 'municipio']),
            models.Index(fields=['latitud', 'longitud']),
            models.Index(fields=['ciudadano', 'estado']),
            models.Index(fields=['creado_en']),
        ]

    def __str__(self):
        return f'Reporte #{str(self.id)[:8]} — {self.barrio} — {self.estado}'

    def calcular_urgencia_automatica(self):
        """Eleva urgencia si la zona tiene muchos reportes recientes."""
        from django.utils import timezone
        from datetime import timedelta
        reportes_recientes = Reporte.objects.filter(
            latitud__range=(float(self.latitud) - 0.005, float(self.latitud) + 0.005),
            longitud__range=(float(self.longitud) - 0.005, float(self.longitud) + 0.005),
            creado_en__gte=timezone.now() - timedelta(hours=48),
            estado__in=[self.ESTADO_PENDIENTE, self.ESTADO_REVISANDO]
        ).count()
        if reportes_recientes >= 5:
            return self.URGENCIA_CRITICA
        elif reportes_recientes >= 3:
            return self.URGENCIA_ALTA
        return self.urgencia


class HistorialEstadoReporte(TimeStampedModel):
    """Log de cambios de estado de un reporte."""
    reporte          = models.ForeignKey(Reporte, on_delete=models.CASCADE,
                                          related_name='historial')
    estado_anterior  = models.CharField(max_length=20, blank=True)
    estado_nuevo     = models.CharField(max_length=20)
    cambiado_por     = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                          null=True)
    notas            = models.TextField(blank=True)

    class Meta:
        db_table = 'historial_estados_reporte'
        ordering = ['-creado_en']
