# gamificacion/models.py

from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class NivelCiudadano(TimeStampedModel):
    """Niveles que el ciudadano puede alcanzar."""
    nombre          = models.CharField(max_length=50)   # Ej: Guardián Verde, Héroe Urbano
    puntos_minimos  = models.IntegerField()
    icono           = models.CharField(max_length=100)  # Emoji o ruta de ícono SVG
    color           = models.CharField(max_length=7)    # Hex
    descripcion     = models.TextField(blank=True)
    beneficios      = models.TextField(blank=True)      # JSON con lista de beneficios

    class Meta:
        db_table = 'niveles_ciudadano'
        ordering = ['puntos_minimos']


class PerfilGamificacion(TimeStampedModel):
    """Perfil de gamificación de un ciudadano (1:1 con Usuario)."""
    usuario          = models.OneToOneField(settings.AUTH_USER_MODEL,
                                             on_delete=models.CASCADE,
                                             related_name='perfil_gamificacion')
    puntos_totales   = models.IntegerField(default=0)
    puntos_canjeados = models.IntegerField(default=0)
    nivel            = models.ForeignKey(NivelCiudadano, on_delete=models.SET_NULL,
                                          null=True, blank=True)
    reportes_validos = models.IntegerField(default=0)   # Reportes que no fueron rechazados
    racha_dias       = models.IntegerField(default=0)   # Días consecutivos con actividad
    ultimo_reporte   = models.DateField(null=True, blank=True)
    posicion_ranking = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'perfiles_gamificacion'

    @property
    def puntos_disponibles(self):
        return self.puntos_totales - self.puntos_canjeados


class TransaccionPuntos(TimeStampedModel):
    """Registro de cada ganancia o canje de puntos."""
    TIPO_GANANCIA = 'ganancia'
    TIPO_CANJE    = 'canje'
    TIPO_BONUS    = 'bonus'
    TIPO_AJUSTE   = 'ajuste'

    TIPOS = [
        (TIPO_GANANCIA, 'Ganancia por reporte'),
        (TIPO_CANJE,    'Canje de recompensa'),
        (TIPO_BONUS,    'Bonus especial'),
        (TIPO_AJUSTE,   'Ajuste administrativo'),
    ]

    perfil       = models.ForeignKey(PerfilGamificacion, on_delete=models.CASCADE,
                                      related_name='transacciones')
    tipo         = models.CharField(max_length=15, choices=TIPOS)
    puntos       = models.IntegerField()  # Positivo = ganancia, negativo = canje
    descripcion  = models.CharField(max_length=200)
    reporte_ref  = models.ForeignKey('reportes.Reporte', on_delete=models.SET_NULL,
                                      null=True, blank=True)
    comercio_ref = models.ForeignKey('comercios.Comercio', on_delete=models.SET_NULL,
                                      null=True, blank=True)
    saldo_despues = models.IntegerField()  # Puntos totales tras la transacción

    class Meta:
        db_table = 'transacciones_puntos'
        ordering = ['-creado_en']


class ConfiguracionPuntos(TimeStampedModel):
    """Configuración del sistema de puntos (editable por admin)."""
    EVENTO_REPORTE_NUEVO        = 'reporte_nuevo'
    EVENTO_REPORTE_RESUELTO     = 'reporte_resuelto'
    EVENTO_REPORTE_CONFIRMADO   = 'reporte_confirmado'
    EVENTO_RACHA_7_DIAS         = 'racha_7_dias'
    EVENTO_PRIMER_REPORTE       = 'primer_reporte'

    evento      = models.CharField(max_length=50, unique=True)
    puntos      = models.IntegerField()
    descripcion = models.CharField(max_length=200)
    activo      = models.BooleanField(default=True)

    class Meta:
        db_table = 'configuracion_puntos'
