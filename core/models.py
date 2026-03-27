# core/models.py
import uuid
from django.db import models

class TimeStampedModel(models.Model):
    """Modelo abstracto base — todos los modelos de LimpioRD lo heredan."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
