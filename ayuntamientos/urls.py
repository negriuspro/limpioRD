# ayuntamientos/urls.py
from django.urls import path
from . import views

app_name = 'ayuntamientos'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('mapa/', views.mapa_calor, name='mapa'),
    path('reportes/', views.lista_reportes, name='reportes'),
    path('reportes/<uuid:reporte_id>/estado/', views.cambiar_estado_reporte, name='cambiar_estado'),
    path('api/puntos/', views.api_puntos_mapa, name='api_puntos'),
    path('api/stats/', views.api_stats_dashboard, name='api_stats'),
]
