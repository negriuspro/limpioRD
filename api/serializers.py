# api/serializers.py
from rest_framework import serializers
from reportes.models import Reporte
from gamificacion.models import PerfilGamificacion

class ReporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reporte
        fields = ['id', 'municipio', 'categoria', 'latitud', 'longitud',
                  'descripcion', 'foto', 'foto_url', 'estado', 'urgencia', 'creado_en']
        read_only_fields = ['estado', 'urgencia', 'creado_en', 'foto_url']

class PerfilSerializer(serializers.ModelSerializer):
    nivel_nombre = serializers.CharField(source='nivel.nombre', read_only=True)

    class Meta:
        model = PerfilGamificacion
        fields = ['puntos_disponibles', 'puntos_totales', 'nivel_nombre', 'reportes_validos']
