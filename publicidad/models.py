# publicidad/models.py

from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Anuncio(TimeStampedModel):
    """Anuncio institucional dentro de la plataforma web."""
    POSICION_BANNER_TOP       = 'banner_top'
    POSICION_SIDEBAR          = 'sidebar'
    POSICION_CARD_MAPA        = 'card_mapa'
    POSICION_PANEL_CIUDADANO  = 'panel_ciudadano'

    POSICIONES = [
        (POSICION_BANNER_TOP,      'Banner superior'),
        (POSICION_SIDEBAR,         'Barra lateral'),
        (POSICION_CARD_MAPA,       'Tarjeta sobre el mapa'),
        (POSICION_PANEL_CIUDADANO, 'Panel del ciudadano'),
    ]

    anunciante      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                         null=True)
    titulo          = models.CharField(max_length=100)
    descripcion     = models.CharField(max_length=250, blank=True)
    imagen          = models.ImageField(upload_to='publicidad/')
    url_destino     = models.URLField()
    posicion        = models.CharField(max_length=30, choices=POSICIONES)
    municipios      = models.ManyToManyField('ayuntamientos.Municipio', blank=True,
                                              help_text='Vacío = todos los municipios')
    activo          = models.BooleanField(default=True)
    fecha_inicio    = models.DateField()
    fecha_fin       = models.DateField()
    impresiones     = models.BigIntegerField(default=0)
    clics           = models.BigIntegerField(default=0)
    presupuesto_mensual = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'anuncios'

    @property
    def ctr(self):
        """Click-Through Rate."""
        if self.impresiones == 0:
            return 0
        return round((self.clics / self.impresiones) * 100, 2)
