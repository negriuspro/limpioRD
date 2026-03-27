import random
from django.core.management.base import BaseCommand
from accounts.models import Usuario
from ayuntamientos.models import Municipio, ZonaCritica
from reportes.models import CategoriaResiduo, Reporte
from gamificacion.models import ConfiguracionPuntos

class Command(BaseCommand):
    help = 'Popula la DB con datos iniciales y mocks para demostración (LimpioRD)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Generando Municipio de Prueba...')
        dn, _ = Municipio.objects.get_or_create(
            codigo='DN',
            defaults={
                'nombre': 'Distrito Nacional',
                'latitud_centro': 18.4861,
                'longitud_centro': -69.9312,
                'plan_suscripcion': Municipio.PLAN_PRO
            }
        )

        self.stdout.write('Generando Configuración de Puntos...')
        ConfiguracionPuntos.objects.get_or_create(evento='reporte_nuevo', defaults={'puntos': 10, 'descripcion': 'Por crear un reporte ciudadano'})
        ConfiguracionPuntos.objects.get_or_create(evento='reporte_resuelto', defaults={'puntos': 25, 'descripcion': 'Al resolverse exitosamente el reporte'})

        self.stdout.write('Generando Categorías de Residuos...')
        cat_plastico, _ = CategoriaResiduo.objects.get_or_create(nombre='Plástico', defaults={'icono': 'archive-box'})
        cat_organico, _ = CategoriaResiduo.objects.get_or_create(nombre='Orgánico', defaults={'icono': 'leaf'})
        cat_escombros, _ = CategoriaResiduo.objects.get_or_create(nombre='Escombros', defaults={'icono': 'home-modern'})

        self.stdout.write('Creando Usuarios...')
        admin, _ = Usuario.objects.get_or_create(
            email='admin@limpiord.com',
            defaults={
                'nombre': 'Admin',
                'apellido': 'Ayuntamiento',
                'rol': Usuario.ROL_ADMIN_AYUNTAMIENTO,
                'municipio': dn,
            }
        )
        admin.set_password('Admin123!')
        admin.save()
        
        ciudadano, _ = Usuario.objects.get_or_create(
            email='ciudadano@limpiord.com',
            defaults={
                'nombre': 'Juan',
                'apellido': 'Pérez',
                'rol': Usuario.ROL_CIUDADANO,
            }
        )
        ciudadano.set_password('Ciudadano123!')
        ciudadano.save()

        self.stdout.write('Generando Reportes Dummy...')
        if not Reporte.objects.exists():
            for i in range(10):
                Reporte.objects.create(
                    ciudadano=ciudadano,
                    municipio=dn,
                    categoria=random.choice([cat_plastico, cat_organico, cat_escombros]),
                    latitud=18.4861 + random.uniform(-0.02, 0.02),
                    longitud=-69.9312 + random.uniform(-0.02, 0.02),
                    descripcion=f'Acumulación de basura en punto {i}',
                    estado=random.choice([Reporte.ESTADO_PENDIENTE, Reporte.ESTADO_RESUELTO])
                )

        self.stdout.write(self.style.SUCCESS('¡Datos iniciales poblados correctamente! Ya puedes probar la plataforma.'))
