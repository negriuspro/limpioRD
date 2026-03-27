# negocios/views.py
from django.shortcuts import render, redirect
from django.db import models
from django.contrib.auth.decorators import login_required
from .services import NegocioService
from .models import Venta, Gasto, Producto, Cliente

@login_required
def dashboard_negocio(request):
    """Vista principal de gestión del negocio."""
    if request.user.rol not in ['comercio', 'admin_sistema']:
        return redirect('/')

    rango = request.GET.get('rango', 'mes')
    resumen = NegocioService.obtener_reporte_financiero(rango)
    
    context = {
        'resumen': resumen,
        'ultimas_ventas': Venta.objects.all().order_by('-creado_en')[:5],
        'ultimos_gastos': Gasto.objects.all().order_by('-creado_en')[:5],
        'productos_bajo_stock': Producto.objects.filter(stock__lte=models.F('stock_minimo'))[:5],
        'rango_actual': rango,
    }
    return render(request, 'negocios/dashboard.html', context)

import csv
from django.http import HttpResponse

@login_required
def exportar_reporte(request):
    """Exporta reporte de ventas en CSV (Regla 7)."""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ventas.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['ID', 'Cliente', 'Total', 'Estado', 'Fecha'])
    
    ventas = Venta.objects.all().order_by('-creado_en')
    for v in ventas:
        writer.writerow([v.id, v.cliente.nombre if v.cliente else 'N/A', v.total, v.estado, v.creado_en])
    
    return response

@login_required
def lista_productos(request):
    productos = Producto.objects.all()
    return render(request, 'negocios/productos.html', {'productos': productos})
