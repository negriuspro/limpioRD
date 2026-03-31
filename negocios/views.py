# negocios/views.py
import csv
from django.shortcuts import render, redirect
from django.db import models
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .services import NegocioService
from .models import Venta, Gasto, Producto, Cliente


def _verificar_comercio(request):
    """Retorna True si el usuario tiene acceso al módulo de negocios."""
    return request.user.rol in ['comercio', 'admin_sistema']


@login_required
def dashboard_negocio(request):
    if not _verificar_comercio(request):
        return redirect('/')
    rango = request.GET.get('rango', 'mes')
    resumen = NegocioService.obtener_reporte_financiero(rango)
    context = {
        'resumen':              resumen,
        'ultimas_ventas':       Venta.objects.all().order_by('-creado_en')[:5],
        'ultimos_gastos':       Gasto.objects.all().order_by('-creado_en')[:5],
        'productos_bajo_stock': Producto.objects.filter(stock__lte=models.F('stock_minimo'))[:5],
        'rango_actual':         rango,
    }
    return render(request, 'negocios/dashboard.html', context)


@login_required
def exportar_reporte(request):
    if not _verificar_comercio(request):
        return redirect('/')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Cliente', 'Total', 'Estado', 'Fecha'])
    for v in Venta.objects.all().order_by('-creado_en'):
        writer.writerow([v.id, v.cliente.nombre if v.cliente else 'N/A', v.total, v.estado, v.creado_en])
    return response


@login_required
def lista_productos(request):
    if not _verificar_comercio(request):
        return redirect('/')
    productos = Producto.objects.all()
    return render(request, 'negocios/productos.html', {'productos': productos})
