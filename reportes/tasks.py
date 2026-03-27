# reportes/tasks.py
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Reporte

@shared_task
def notificar_ciudadano_cambio_estado(reporte_id, estado_anterior, estado_nuevo):
    """Envía un email o push notification al ciudadano sobre su reporte."""
    try:
        reporte = Reporte.objects.select_related('ciudadano').get(id=reporte_id)
        if not reporte.ciudadano or not reporte.ciudadano.email:
            return

        asunto = f"Actualización de tu reporte LimpioRD #{str(reporte.id)[:8]}"
        mensaje = f"Hola {reporte.ciudadano.nombre},\n\nTu reporte ha pasado de '{estado_anterior}' a '{estado_nuevo}'.\nGracias por mantener limpia tu ciudad."

        # Simulación de envío de correo
        # send_mail(asunto, mensaje, settings.DEFAULT_FROM_EMAIL, [reporte.ciudadano.email])
        
        # Opcional: Notificación push vía Channels o Firebase
        print(f"Notificación enviada a {reporte.ciudadano.email}")
    except Reporte.DoesNotExist:
        pass
