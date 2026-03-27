# core/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import TimeStampedModel, AuditLog
from .utils import registrar_auditoria
import threading

# Hilera de ejecución para capturar el usuario actual (simplificado para demo)
_thread_locals = threading.local()

@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """Auditoría automática para modelos que heredan de TimeStampedModel."""
    if not isinstance(instance, TimeStampedModel) or isinstance(instance, AuditLog):
        return

    usuario = getattr(_thread_locals, 'user', None)
    accion = AuditLog.ACCION_CREAR if created else AuditLog.ACCION_EDITAR
    
    # Solo registramos si tenemos un usuario (opcional: registrar acciones de sistema)
    registrar_auditoria(usuario, instance, accion)

@receiver(post_delete)
def audit_post_delete(sender, instance, **kwargs):
    if not isinstance(instance, TimeStampedModel) or isinstance(instance, AuditLog):
        return
    
    usuario = getattr(_thread_locals, 'user', None)
    registrar_auditoria(usuario, instance, AuditLog.ACCION_ELIMINAR)
