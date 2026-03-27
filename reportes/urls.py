# reportes/urls.py
from django.urls import path
from . import views

app_name = 'reportes'

urlpatterns = [
    path('dashboard/', views.dashboard_ciudadano, name='dashboard_ciudadano'),
    path('crear/', views.crear_reporte, name='crear_reporte'),
    path('mis-reportes/', views.mis_reportes, name='mis_reportes'),
    path('mis-reportes/<uuid:reporte_id>/', views.detalle_reporte, name='detalle_reporte'),
    path('mis-puntos/', views.mis_puntos, name='mis_puntos'),
]
