# negocios/models.py
from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Cliente(TimeStampedModel):
    """Gestión de Clientes."""
    nombre = models.CharField(max_length=150)
    documento = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'negocio_clientes'


class Proveedor(TimeStampedModel):
    """Gestión de Proveedores."""
    nombre = models.CharField(max_length=150)
    rnc = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'negocio_proveedores'


class Producto(TimeStampedModel):
    """Gestión de Productos / Inventario."""
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=5)
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, related_name='productos')

    def __str__(self):
        return f'{self.nombre} ({self.codigo})'

    class Meta:
        db_table = 'negocio_productos'


class Venta(TimeStampedModel):
    """Registro de Ventas."""
    ESTADO_PAGADO = 'pagado'
    ESTADO_PENDIENTE = 'pendiente'
    ESTADO_CANCELADO = 'cancelado'

    ESTADOS = [
        (ESTADO_PAGADO, 'Pagado'),
        (ESTADO_PENDIENTE, 'Pendiente'),
        (ESTADO_CANCELADO, 'Cancelado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, related_name='ventas')
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ventas_realizadas')

    def __str__(self):
        return f'Venta #{self.id} - {self.total}'

    class Meta:
        db_table = 'negocio_ventas'


class DetalleVenta(TimeStampedModel):
    """Detalle de productos en una venta."""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'negocio_detalles_venta'


class Gasto(TimeStampedModel):
    """Registro de Gastos."""
    ESTADO_PAGADO = 'pagado'
    ESTADO_PENDIENTE = 'pendiente'

    ESTADOS = [
        (ESTADO_PAGADO, 'Pagado'),
        (ESTADO_PENDIENTE, 'Pendiente'),
    ]

    descripcion = models.CharField(max_length=255)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_gasto = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PAGADO)
    categoria = models.CharField(max_length=100) # Ej: Servicios, Equipos, Nomad, etc.

    def __str__(self):
        return f'Gasto: {self.descripcion} - {self.monto}'

    class Meta:
        db_table = 'negocio_gastos'
