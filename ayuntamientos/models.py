# ayuntamientos/models.py

from django.db import models
from core.models import TimeStampedModel

class Municipio(TimeStampedModel):
    """Representa un ayuntamiento/municipio suscrito a LimpioRD."""

    PLAN_BASICO = 'basico'
    PLAN_PRO    = 'pro'
    PLAN_LIBRE  = 'libre'

    PLANES = [
        (PLAN_LIBRE,  'Libre (Demo)'),
        (PLAN_BASICO, 'Básico — RD$15,000/mes'),
        (PLAN_PRO,    'Pro — RD$28,000/mes'),
    ]

    nombre             = models.CharField(max_length=150)
    codigo             = models.CharField(max_length=10, unique=True)  # ej: SDN, SDE, SDO
    logo               = models.ImageField(upload_to='municipios/logos/', blank=True)
    latitud_centro     = models.DecimalField(max_digits=9, decimal_places=6)
    longitud_centro    = models.DecimalField(max_digits=9, decimal_places=6)
    plan_suscripcion   = models.CharField(max_length=10, choices=PLANES, default=PLAN_LIBRE)
    fecha_inicio_plan  = models.DateField(null=True, blank=True)
    fecha_fin_plan     = models.DateField(null=True, blank=True)
    contacto_principal = models.EmailField(blank=True)
    telefono_contacto  = models.CharField(max_length=20, blank=True)
    esta_activo        = models.BooleanField(default=True)
    descripcion        = models.TextField(blank=True)

    class Meta:
        db_table = 'municipios'
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'

    def __str__(self):
        return self.nombre

    @property
    def suscripcion_vigente(self):
        from django.utils import timezone
        if not self.fecha_fin_plan:
            return False
        return self.fecha_fin_plan >= timezone.now().date()

    @property
    def precio_plan(self):
        precios = {'basico': 15000, 'pro': 28000, 'libre': 0}
        return precios.get(self.plan_suscripcion, 0)


class ZonaCritica(TimeStampedModel):
    """Zona dentro de un municipio con historial de acumulación."""
    municipio        = models.ForeignKey(Municipio, on_delete=models.CASCADE, related_name='zonas')
    nombre           = models.CharField(max_length=150)
    latitud          = models.DecimalField(max_digits=9, decimal_places=6)
    longitud         = models.DecimalField(max_digits=9, decimal_places=6)
    radio_metros     = models.IntegerField(default=500)
    nivel_prioridad  = models.IntegerField(default=1)  # 1=baja, 2=media, 3=alta, 4=crítica
    total_reportes   = models.IntegerField(default=0)  # Desnormalizado para performance

    class Meta:
        db_table = 'zonas_criticas'
