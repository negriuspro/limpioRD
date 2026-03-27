# negocios/services.py
from decimal import Decimal
from django.db import transaction, models
from django.utils import timezone
from .models import Venta, DetalleVenta, Gasto, Producto, Cliente
from core.utils import registrar_auditoria

class NegocioService:
    @staticmethod
    @transaction.atomic
    def registrar_venta(datos_venta, productos_detalle, usuario):
        """
        Registra una venta con sus detalles y actualiza stock.
        datos_venta: dict con cliente_id y estado.
        productos_detalle: list de dicts con producto_id y cantidad.
        """
        venta = Venta.objects.create(
            cliente_id=datos_venta.get('cliente_id'),
            estado=datos_venta.get('estado', Venta.ESTADO_PAGADO),
            vendedor=usuario
        )

        total_venta = Decimal('0.00')
        for item in productos_detalle:
            producto = Producto.objects.get(id=item['producto_id'])
            cantidad = item['cantidad']
            
            # Validar stock
            if producto.stock < cantidad:
                raise ValueError(f"Stock insuficiente para {producto.nombre}")

            subtotal = producto.precio_venta * Decimal(str(cantidad))
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio_venta,
                subtotal=subtotal
            )
            
            # Actualizar stock
            producto.stock -= cantidad
            producto.save()
            
            total_venta += subtotal

        venta.total = total_venta
        venta.save()

        # Auditoría (Regla 8)
        registrar_auditoria(usuario, venta, 'crear', detalles={'total': str(total_venta)})
        
        return venta

    @staticmethod
    def obtener_reporte_financiero(rango='mes'):
        """
        Genera resumen financiero según el rango solicitado (Regla 7).
        """
        ahora = timezone.now()
        if rango == 'dia':
            inicio = ahora.replace(hour=0, minute=0, second=0, microsecond=0)
        elif rango == 'semana':
            inicio = ahora - timezone.timedelta(days=7)
        elif rango == 'trimestre':
            inicio = ahora - timezone.timedelta(days=90)
        elif rango == 'semestre':
            inicio = ahora - timezone.timedelta(days=180)
        elif rango == 'año':
            inicio = ahora.replace(month=1, day=1)
        else: # mes por defecto
            inicio = ahora.replace(day=1)

        ingresos = Venta.objects.filter(creado_en__gte=inicio, estado=Venta.ESTADO_PAGADO).aggregate(models.Sum('total'))['total__sum'] or Decimal('0.00')
        gastos = Gasto.objects.filter(creado_en__gte=inicio).aggregate(models.Sum('monto'))['monto__sum'] or Decimal('0.00')
        
        return {
            'ingresos': ingresos,
            'gastos': gastos,
            'balance': ingresos - gastos,
            'rango': rango
        }
