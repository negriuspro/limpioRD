from django.contrib import admin
from .models import NivelCiudadano, PerfilGamificacion, TransaccionPuntos, ConfiguracionPuntos


@admin.register(NivelCiudadano)
class NivelCiudadanoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'puntos_minimos', 'color')
    ordering     = ('puntos_minimos',)


@admin.register(PerfilGamificacion)
class PerfilGamificacionAdmin(admin.ModelAdmin):
    list_display  = ('usuario', 'puntos_totales', 'puntos_canjeados', 'reportes_validos', 'nivel')
    search_fields = ('usuario__email', 'usuario__nombre')
    list_filter   = ('nivel',)


@admin.register(TransaccionPuntos)
class TransaccionPuntosAdmin(admin.ModelAdmin):
    list_display  = ('perfil', 'tipo', 'puntos', 'descripcion', 'creado_en')
    list_filter   = ('tipo',)
    search_fields = ('perfil__usuario__email',)


@admin.register(ConfiguracionPuntos)
class ConfiguracionPuntosAdmin(admin.ModelAdmin):
    list_display = ('evento', 'puntos', 'activo')
    list_filter  = ('activo',)
