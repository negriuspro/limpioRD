from django.contrib import admin
from .models import Comercio, Recompensa, CanjeRecompensa


@admin.register(Comercio)
class ComercioAdmin(admin.ModelAdmin):
    list_display  = ('nombre_comercial', 'municipio', 'esta_activo', 'membresía_activa')
    list_filter   = ('esta_activo', 'membresía_activa', 'municipio')
    search_fields = ('nombre_comercial', 'rif')


@admin.register(Recompensa)
class RecompensaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'comercio', 'tipo', 'puntos_requeridos', 'activo')
    list_filter  = ('tipo', 'activo')


@admin.register(CanjeRecompensa)
class CanjeRecompensaAdmin(admin.ModelAdmin):
    list_display = ('ciudadano', 'recompensa', 'codigo_canje', 'usado', 'puntos_usados')
    list_filter  = ('usado',)
