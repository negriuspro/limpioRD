# negocios/urls.py
from django.urls import path
from . import views

app_name = 'negocios'

urlpatterns = [
    path('dashboard/', views.dashboard_negocio, name='dashboard'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('exportar/', views.exportar_reporte, name='exportar_reporte'),
]
