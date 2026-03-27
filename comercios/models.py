# comercios/models.py

from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Comercio(TimeStampedModel):
    """Comercio que paga membresía para aparecer en catálogo de recompensas."""
    usuario          = models.OneToOneField(settings.AUTH_USER_MODEL,
                                             on_delete=models.CASCADE, related_name='comercio')
    nombre_comercial = models.CharField(max_length=150)
    rif              = models.CharField(max_length=20, blank=True)
    descripcion      = models.TextField(blank=True)
    logo             = models.ImageField(upload_to='comercios/logos/', blank=True)
    direccion        = models.CharField(max_length=300)
    barrio           = models.CharField(max_length=100)
    municipio        = models.ForeignKey('ayuntamientos.Municipio', on_delete=models.SET_NULL,
                                          null=True)
    telefono         = models.CharField(max_length=20)
    sitio_web        = models.URLField(blank=True)
    esta_activo      = models.BooleanField(default=True)
    membresía_activa = models.BooleanField(default=False)
    fecha_inicio_membresia = models.DateField(null=True, blank=True)
    fecha_fin_membresia    = models.DateField(null=True, blank=True)
    precio_membresia_mensual = models.DecimalField(max_digits=10, decimal_places=2,
                                                    default=5000)

    class Meta:
        db_table = 'comercios'


class Recompensa(TimeStampedModel):
    """Beneficio que un comercio ofrece a cambio de puntos LimpioRD."""
    TIPO_DESCUENTO  = 'descuento_porcentaje'
    TIPO_PRODUCTO   = 'producto_gratis'
    TIPO_SERVICIO   = 'servicio'

    TIPOS = [
        (TIPO_DESCUENTO, 'Descuento porcentual'),
        (TIPO_PRODUCTO,  'Producto gratis'),
        (TIPO_SERVICIO,  'Servicio'),
    ]

    comercio            = models.ForeignKey(Comercio, on_delete=models.CASCADE,
                                             related_name='recompensas')
    titulo              = models.CharField(max_length=150)
    descripcion         = models.TextField()
    tipo                = models.CharField(max_length=30, choices=TIPOS)
    valor_descuento     = models.DecimalField(max_digits=5, decimal_places=2, null=True,
                                               blank=True, help_text='% si es descuento')
    puntos_requeridos   = models.IntegerField()
    stock               = models.IntegerField(default=-1)  # -1 = ilimitado
    canjes_totales      = models.IntegerField(default=0)
    activo              = models.BooleanField(default=True)
    fecha_vencimiento   = models.DateField(null=True, blank=True)
    imagen              = models.ImageField(upload_to='recompensas/', blank=True)

    class Meta:
        db_table = 'recompensas'


class CanjeRecompensa(TimeStampedModel):
    """Registro de un canje realizado por un ciudadano."""
    ciudadano   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                     related_name='canjes')
    recompensa  = models.ForeignKey(Recompensa, on_delete=models.CASCADE,
                                     related_name='canjes')
    codigo_canje = models.CharField(max_length=20, unique=True)  # Código para validar en comercio
    usado       = models.BooleanField(default=False)
    usado_en    = models.DateTimeField(null=True, blank=True)
    puntos_usados = models.IntegerField()

    class Meta:
        db_table = 'canjes_recompensas'
