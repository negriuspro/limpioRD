# core/models.py
import uuid
from django.db import models
from django.conf import settings

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class TimeStampedModel(models.Model):
    """Modelo abstracto base — todos los modelos de LimpioRD lo heredan."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    def delete(self, **kwargs):
        self.is_deleted = True
        self.save()

    def hard_delete(self, **kwargs):
        super().delete(**kwargs)

    class Meta:
        abstract = True


class AuditLog(models.Model):
    """Registro de auditoría global — no se hereda, se usa para guardar logs."""
    ACCION_CREAR   = 'crear'
    ACCION_EDITAR  = 'editar'
    ACCION_ELIMINAR = 'eliminar'

    ACCIONES = [
        (ACCION_CREAR,    'Creación'),
        (ACCION_EDITAR,   'Edición'),
        (ACCION_ELIMINAR, 'Eliminar (Soft Delete)'),
    ]

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    modelo       = models.CharField(max_length=100)
    objeto_id    = models.CharField(max_length=100)
    accion       = models.CharField(max_length=20, choices=ACCIONES)
    detalles     = models.JSONField(null=True, blank=True)
    creado_en    = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'auditoria_logs'
        ordering = ['-creado_en']

    def __str__(self):
        return f'{self.usuario} — {self.accion} {self.modelo} ({self.creado_en})'
