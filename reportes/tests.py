from django.test import TestCase
from accounts.models import Usuario
from ayuntamientos.models import Municipio
from reportes.models import Reporte, CategoriaResiduo
from reportes.services import ReporteService

class ReporteLogicTest(TestCase):
    def setUp(self):
        self.ciudadano = Usuario.objects.create(email='ciudadano@test.com', rol=Usuario.ROL_CIUDADANO)
        self.admin = Usuario.objects.create(email='admin@test.com', rol=Usuario.ROL_ADMIN_AYUNTAMIENTO)
        self.municipio = Municipio.objects.create(codigo='TEST', nombre='TestCity', latitud_centro=0, longitud_centro=0)
        self.cat = CategoriaResiduo.objects.create(nombre='Plástico')

    def test_creacion_reporte_y_estado(self):
        datos = {
            'municipio_id': self.municipio.id,
            'categoria_id': self.cat.id,
            'latitud': 18.0,
            'longitud': -69.0,
            'descripcion': 'Mucha basura'
        }
        reporte = ReporteService.crear_reporte(datos, self.ciudadano)
        self.assertEqual(reporte.estado, Reporte.ESTADO_PENDIENTE)
        self.assertEqual(Reporte.objects.count(), 1)

        # Test state change
        reporte_actualizado = ReporteService.cambiar_estado(reporte.id, Reporte.ESTADO_RESUELTO, self.admin)
        self.assertEqual(reporte_actualizado.estado, Reporte.ESTADO_RESUELTO)
