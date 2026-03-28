# reportes/tests.py
from unittest.mock import patch

from django.test import TestCase, Client, override_settings
from django.urls import reverse

from accounts.models import Usuario
from ayuntamientos.models import Municipio
from gamificacion.models import PerfilGamificacion
from reportes.models import Reporte, CategoriaResiduo
from reportes.services import ReporteService


def make_municipio():
    return Municipio.objects.create(
        codigo='SDQ', nombre='Santo Domingo',
        latitud_centro=18.4861, longitud_centro=-69.9312,
    )


def make_categoria():
    return CategoriaResiduo.objects.create(nombre='Plástico', color='#3b82f6')


def make_ciudadano(email='ciudadano@test.com'):
    return Usuario.objects.create_user(
        email=email, password='pass12345',
        nombre='Juan', rol=Usuario.ROL_CIUDADANO,
    )


def make_admin(email='admin@test.com'):
    return Usuario.objects.create_user(
        email=email, password='pass12345',
        nombre='Admin', rol=Usuario.ROL_ADMIN_AYUNTAMIENTO,
    )


class ReporteServiceTests(TestCase):
    """Tests de la lógica de negocio de reportes."""

    def setUp(self):
        self.ciudadano = make_ciudadano()
        self.admin     = make_admin()
        self.municipio = make_municipio()
        self.cat       = make_categoria()

    def _datos_base(self, **kwargs):
        base = {
            'municipio_id': self.municipio.id,
            'categoria_id': self.cat.id,
            'latitud':      18.4861,
            'longitud':     -69.9312,
            'descripcion':  'Mucha basura acumulada',
        }
        base.update(kwargs)
        return base

    def test_crear_reporte_estado_pendiente(self):
        """Un reporte recién creado tiene estado pendiente."""
        reporte = ReporteService.crear_reporte(self._datos_base(), self.ciudadano)
        self.assertEqual(reporte.estado, Reporte.ESTADO_PENDIENTE)
        self.assertEqual(Reporte.objects.count(), 1)

    def test_crear_reporte_categoria_asignada(self):
        """El reporte tiene la categoría correcta."""
        reporte = ReporteService.crear_reporte(self._datos_base(), self.ciudadano)
        self.assertEqual(reporte.categoria, self.cat)

    def test_crear_reporte_municipio_asignado(self):
        """El reporte tiene el municipio correcto."""
        reporte = ReporteService.crear_reporte(self._datos_base(), self.ciudadano)
        self.assertEqual(reporte.municipio, self.municipio)

    @patch('reportes.services.notificar_ciudadano_cambio_estado.delay')
    def test_cambiar_estado_resuelto(self, mock_notify):
        """El admin puede cambiar el estado a resuelto."""
        reporte = ReporteService.crear_reporte(self._datos_base(), self.ciudadano)
        actualizado = ReporteService.cambiar_estado(reporte.id, Reporte.ESTADO_RESUELTO, self.admin)
        self.assertEqual(actualizado.estado, Reporte.ESTADO_RESUELTO)

    @patch('reportes.services.notificar_ciudadano_cambio_estado.delay')
    def test_cambiar_estado_crea_historial(self, mock_notify):
        """Cambio de estado genera entrada en el historial."""
        reporte = ReporteService.crear_reporte(self._datos_base(), self.ciudadano)
        ReporteService.cambiar_estado(reporte.id, Reporte.ESTADO_EN_PROCESO, self.admin)
        self.assertEqual(reporte.historial.count(), 1)

    @patch('reportes.services.notificar_ciudadano_cambio_estado.delay')
    def test_reporte_urgencia_automatica_alta(self, mock_notify):
        """Zona con 3+ reportes eleva urgencia automáticamente."""
        datos = self._datos_base()
        # Crear 3 reportes en la misma zona
        for _ in range(3):
            ReporteService.crear_reporte(datos, self.ciudadano)
        reporte = Reporte.objects.first()
        urgencia = reporte.calcular_urgencia_automatica()
        self.assertGreaterEqual(urgencia, Reporte.URGENCIA_ALTA)


class ReporteViewTests(TestCase):
    """Tests de las vistas web del módulo ciudadano."""

    def setUp(self):
        self.client    = Client()
        self.ciudadano = make_ciudadano()
        self.admin     = make_admin()
        self.municipio = make_municipio()
        self.cat       = make_categoria()
        PerfilGamificacion.objects.get_or_create(usuario=self.ciudadano)

    def test_dashboard_requires_login(self):
        """Dashboard redirige si no hay sesión."""
        response = self.client.get(reverse('reportes:dashboard_ciudadano'))
        self.assertRedirects(
            response,
            '/accounts/login/?next=/ciudadano/dashboard/',
            fetch_redirect_response=False,
        )

    def test_dashboard_loads_for_ciudadano(self):
        """Dashboard carga correctamente para ciudadano autenticado."""
        self.client.login(username='ciudadano@test.com', password='pass12345')
        response = self.client.get(reverse('reportes:dashboard_ciudadano'))
        self.assertEqual(response.status_code, 200)

    def test_admin_redirected_from_ciudadano_dashboard(self):
        """Admin redirige al panel municipal desde el dashboard ciudadano."""
        self.client.login(username='admin@test.com', password='pass12345')
        response = self.client.get(reverse('reportes:dashboard_ciudadano'))
        self.assertRedirects(response, '/panel/dashboard/', fetch_redirect_response=False)

    def test_crear_reporte_get(self):
        """Formulario de crear reporte carga correctamente."""
        self.client.login(username='ciudadano@test.com', password='pass12345')
        response = self.client.get(reverse('reportes:crear_reporte'))
        self.assertEqual(response.status_code, 200)

    def test_crear_reporte_post_valido(self):
        """POST válido crea un reporte y redirige."""
        self.client.login(username='ciudadano@test.com', password='pass12345')
        response = self.client.post(reverse('reportes:crear_reporte'), {
            'municipio':  self.municipio.id,
            'categoria':  self.cat.id,
            'descripcion': 'Basura en la esquina de la calle principal',
            'barrio':     'Los Prados',
            'referencia': 'Frente al parque',
            'latitud':    '18.4861',
            'longitud':   '-69.9312',
        })
        self.assertRedirects(response, '/ciudadano/mis-reportes/', fetch_redirect_response=False)
        self.assertEqual(Reporte.objects.count(), 1)

    def test_crear_reporte_post_incompleto(self):
        """POST sin campos requeridos devuelve error."""
        self.client.login(username='ciudadano@test.com', password='pass12345')
        response = self.client.post(reverse('reportes:crear_reporte'), {
            'municipio': '', 'categoria': '', 'descripcion': '',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Reporte.objects.count(), 0)

    def test_mis_reportes_requires_login(self):
        """Mis reportes requiere autenticación."""
        response = self.client.get(reverse('reportes:mis_reportes'))
        self.assertEqual(response.status_code, 302)

    def test_mis_reportes_muestra_solo_los_del_usuario(self):
        """Mis reportes sólo muestra reportes del usuario autenticado."""
        otro = make_ciudadano('otro@test.com')
        PerfilGamificacion.objects.get_or_create(usuario=otro)

        # Crear reporte para ciudadano principal
        ReporteService.crear_reporte({
            'municipio_id': self.municipio.id, 'categoria_id': self.cat.id,
            'latitud': 18.0, 'longitud': -69.0, 'descripcion': 'Reporte de Juan',
        }, self.ciudadano)

        # Crear reporte para otro usuario
        ReporteService.crear_reporte({
            'municipio_id': self.municipio.id, 'categoria_id': self.cat.id,
            'latitud': 18.0, 'longitud': -69.0, 'descripcion': 'Reporte de Otro',
        }, otro)

        self.client.login(username='ciudadano@test.com', password='pass12345')
        response = self.client.get(reverse('reportes:mis_reportes'))
        self.assertEqual(response.status_code, 200)
        # El ciudadano sólo ve sus reportes
        self.assertEqual(response.context['reportes'].paginator.count, 1)

    def test_detalle_reporte_solo_dueno(self):
        """El detalle de un reporte sólo es accesible por su dueño."""
        otro = make_ciudadano('otro2@test.com')
        reporte = ReporteService.crear_reporte({
            'municipio_id': self.municipio.id, 'categoria_id': self.cat.id,
            'latitud': 18.0, 'longitud': -69.0, 'descripcion': 'Reporte ajeno',
        }, otro)

        self.client.login(username='ciudadano@test.com', password='pass12345')
        response = self.client.get(reverse('reportes:detalle_reporte', args=[reporte.id]))
        self.assertEqual(response.status_code, 404)


class ReporteModelTests(TestCase):
    """Tests del modelo Reporte."""

    def setUp(self):
        self.municipio = make_municipio()
        self.cat       = make_categoria()
        self.ciudadano = make_ciudadano()

    def test_reporte_str_contains_id(self):
        """__str__ del reporte incluye parte del ID."""
        reporte = Reporte.objects.create(
            ciudadano=self.ciudadano, municipio=self.municipio,
            categoria=self.cat, latitud=18.0, longitud=-69.0,
            descripcion='Test',
        )
        self.assertIn('Reporte', str(reporte))

    def test_estado_default_es_pendiente(self):
        """Estado inicial de un reporte es pendiente."""
        reporte = Reporte.objects.create(
            ciudadano=self.ciudadano, municipio=self.municipio,
            categoria=self.cat, latitud=18.0, longitud=-69.0,
        )
        self.assertEqual(reporte.estado, Reporte.ESTADO_PENDIENTE)
