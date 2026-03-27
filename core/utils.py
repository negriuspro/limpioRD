# core/utils.py
from django.contrib.contenttypes.models import ContentType
from .models import AuditLog

def registrar_auditoria(usuario, objeto, accion, detalles=None):
    """Registra una acción en el log de auditoría."""
    AuditLog.objects.create(
        usuario=usuario,
        modelo=objeto.__class__.__name__,
        objeto_id=str(objeto.id),
        accion=accion,
        detalles=detalles
    )
