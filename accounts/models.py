# accounts/models.py

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from core.models import TimeStampedModel

class UsuarioManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('rol', Usuario.ROL_ADMIN_SISTEMA)
        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    """
    Modelo de usuario personalizado con roles.
    Roles posibles: ciudadano, funcionario_municipal, admin_ayuntamiento,
                    comercio, admin_sistema
    """
    ROL_CIUDADANO         = 'ciudadano'
    ROL_FUNCIONARIO       = 'funcionario_municipal'
    ROL_ADMIN_AYUNTAMIENTO = 'admin_ayuntamiento'
    ROL_COMERCIO          = 'comercio'
    ROL_ADMIN_SISTEMA     = 'admin_sistema'

    ROLES = [
        (ROL_CIUDADANO,          'Ciudadano'),
        (ROL_FUNCIONARIO,        'Funcionario Municipal'),
        (ROL_ADMIN_AYUNTAMIENTO, 'Administrador de Ayuntamiento'),
        (ROL_COMERCIO,           'Comercio Aliado'),
        (ROL_ADMIN_SISTEMA,      'Administrador del Sistema'),
    ]

    email           = models.EmailField(unique=True, db_index=True)
    nombre          = models.CharField(max_length=100)
    apellido        = models.CharField(max_length=100)
    telefono        = models.CharField(max_length=20, blank=True)
    cedula          = models.CharField(max_length=20, blank=True)
    edad            = models.PositiveSmallIntegerField(null=True, blank=True)
    rol             = models.CharField(max_length=30, choices=ROLES, default=ROL_CIUDADANO)
    avatar          = models.ImageField(upload_to='avatars/', blank=True, null=True)
    barrio          = models.CharField(max_length=100, blank=True)
    municipio       = models.ForeignKey('ayuntamientos.Municipio', on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='usuarios')
    esta_activo     = models.BooleanField(default=True)
    email_verificado = models.BooleanField(default=False)
    ultimo_acceso   = models.DateTimeField(null=True, blank=True)

    is_active  = models.BooleanField(default=True)
    is_staff   = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        indexes = [
            models.Index(fields=['rol']),
            models.Index(fields=['municipio']),
        ]

    def __str__(self):
        return f'{self.nombre} {self.apellido} ({self.email})'

    @property
    def nombre_completo(self):
        return f'{self.nombre} {self.apellido}'

    @property
    def es_ciudadano(self):
        return self.rol == self.ROL_CIUDADANO

    @property
    def es_funcionario(self):
        return self.rol in [self.ROL_FUNCIONARIO, self.ROL_ADMIN_AYUNTAMIENTO]

    @property
    def es_admin_sistema(self):
        return self.rol == self.ROL_ADMIN_SISTEMA
