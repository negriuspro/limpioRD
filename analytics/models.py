# analytics/models.py

from django.db import models
from core.models import TimeStampedModel

class EstadisticaDiaria(TimeStampedModel):
    """
    Snapshot diario de métricas por municipio.
    Generado automáticamente por tarea Celery cada medianoche.
    """
    municipio            = models.ForeignKey('ayuntamientos.Municipio',
                                              on_delete=models.CASCADE,
                                              related_name='estadisticas')
    fecha                = models.DateField()
    total_reportes       = models.IntegerField(default=0)
    reportes_resueltos   = models.IntegerField(default=0)
    reportes_pendientes  = models.IntegerField(default=0)
    tiempo_respuesta_promedio_horas = models.DecimalField(max_digits=6, decimal_places=2,
                                                           default=0)
    nuevos_usuarios      = models.IntegerField(default=0)
    usuarios_activos     = models.IntegerField(default=0)
    puntos_otorgados     = models.IntegerField(default=0)
    zona_mas_activa      = models.CharField(max_length=150, blank=True)

    class Meta:
        db_table = 'estadisticas_diarias'
        unique_together = [('municipio', 'fecha')]
        ordering = ['-fecha']


class InformeAmbiental(TimeStampedModel):
    """Informe generado para venta a ONGs y organismos."""
    titulo       = models.CharField(max_length=200)
    periodo_inicio = models.DateField()
    periodo_fin  = models.DateField()
    municipios   = models.ManyToManyField('ayuntamientos.Municipio')
    archivo_pdf  = models.FileField(upload_to='informes/', blank=True)
    precio       = models.DecimalField(max_digits=10, decimal_places=2, default=10000)
    publicado    = models.BooleanField(default=False)
    resumen_ejecutivo = models.TextField(blank=True)

    class Meta:
        db_table = 'informes_ambientales'
