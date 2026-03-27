from django.test import TestCase
from accounts.models import Usuario
from gamificacion.models import ConfiguracionPuntos
from gamificacion.services import PuntosService

class GamificacionServiceTest(TestCase):
    def setUp(self):
        self.user = Usuario.objects.create(email='test@limpiord.com', nombre='Test', apellido='Test')
        ConfiguracionPuntos.objects.create(evento='reporte_nuevo', puntos=15, descripcion='Test')

    def test_otorgar_puntos(self):
        puntos = PuntosService.otorgar_puntos(self.user, 'reporte_nuevo')
        self.assertEqual(puntos, 15)
        
        # Verify profile is updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.perfil_gamificacion.puntos_totales, 15)
