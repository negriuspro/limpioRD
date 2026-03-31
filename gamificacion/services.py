# gamificacion/services.py
from django.db import transaction
from .models import PerfilGamificacion, TransaccionPuntos, ConfiguracionPuntos, NivelCiudadano

class PuntosService:
    @staticmethod
    @transaction.atomic
    def otorgar_puntos(usuario, evento_codigo, reporte=None):
        try:
            config = ConfiguracionPuntos.objects.get(evento=evento_codigo, activo=True)
            puntos = config.puntos
        except ConfiguracionPuntos.DoesNotExist:
            puntos = 10  # Fallback

        perfil, _ = PerfilGamificacion.objects.get_or_create(usuario=usuario)
        perfil.puntos_totales += puntos
        
        # Subir de nivel si aplica
        niveles = NivelCiudadano.objects.filter(puntos_minimos__lte=perfil.puntos_totales).order_by('-puntos_minimos')
        if niveles.exists():
            perfil.nivel = niveles.first()
            
        perfil.save()

        TransaccionPuntos.objects.create(
            perfil=perfil,
            tipo=TransaccionPuntos.TIPO_GANANCIA,
            puntos=puntos,
            descripcion=f"Ganancia por {evento_codigo}",
            reporte_ref=reporte,
            saldo_despues=perfil.puntos_totales
        )
        return puntos

    @staticmethod
    @transaction.atomic
    def canjear_recompensa(usuario, recompensa):
        perfil = usuario.perfil_gamificacion
        if perfil.puntos_disponibles < recompensa.puntos_requeridos:
            raise ValueError("Puntos insuficientes")
            
        if recompensa.stock == 0:
            raise ValueError("Recompensa agotada")

        # Restar stock y guardar canje
        perfil.puntos_canjeados += recompensa.puntos_requeridos
        perfil.save()

        if recompensa.stock > 0:
            recompensa.stock -= 1
        recompensa.canjes_totales += 1
        recompensa.save()

        from comercios.models import CanjeRecompensa
        import uuid
        canje = CanjeRecompensa.objects.create(
            ciudadano=usuario,
            recompensa=recompensa,
            codigo_canje=str(uuid.uuid4())[:8].upper(),
            puntos_usados=recompensa.puntos_requeridos
        )

        TransaccionPuntos.objects.create(
            perfil=perfil,
            tipo=TransaccionPuntos.TIPO_CANJE,
            puntos=-recompensa.puntos_requeridos,
            descripcion=f"Canje: {recompensa.titulo}",
            comercio_ref=recompensa.comercio,
            saldo_despues=perfil.puntos_disponibles
        )
        return canje
