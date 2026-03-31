# accounts/tests.py
from django.test import TestCase, Client
from django.urls import reverse

from ayuntamientos.models import Municipio
from .models import Usuario


class AuthViewTests(TestCase):
    """Tests de autenticación: login, signup, logout."""

    def setUp(self):
        self.client = Client()
        self.municipio = Municipio.objects.create(
            nombre='Distrito Nacional',
            codigo='DN-TEST',
            latitud_centro='18.4861',
            longitud_centro='-69.9312',
            esta_activo=True,
        )
        self.user = Usuario.objects.create_user(
            email='test@limpiord.com',
            password='TestPass123!',
            nombre='Juan',
            apellido='Pérez',
            rol=Usuario.ROL_CIUDADANO,
        )

    # ── Login ─────────────────────────────────────────────────────
    def test_login_page_loads(self):
        """La página de login carga con código 200."""
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar Sesión')

    def test_login_valid_credentials(self):
        """Login exitoso redirige al dashboard ciudadano."""
        response = self.client.post(reverse('accounts:login'), {
            'email':    'test@limpiord.com',
            'password': 'TestPass123!',
        })
        self.assertRedirects(response, '/ciudadano/dashboard/', fetch_redirect_response=False)

    def test_login_invalid_password(self):
        """Login con contraseña incorrecta devuelve error."""
        response = self.client.post(reverse('accounts:login'), {
            'email':    'test@limpiord.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)
        messages_list = list(response.wsgi_request._messages)
        self.assertTrue(len(messages_list) > 0)

    def test_login_empty_fields(self):
        """Login con campos vacíos devuelve 200 (no redirige)."""
        response = self.client.post(reverse('accounts:login'), {
            'email': '', 'password': '',
        })
        self.assertEqual(response.status_code, 200)

    def test_login_authenticated_user_redirects(self):
        """Usuario ya autenticado es redirigido desde login."""
        self.client.login(username='test@limpiord.com', password='TestPass123!')
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 302)

    # ── Signup ────────────────────────────────────────────────────
    def test_signup_page_loads(self):
        """Página de registro carga correctamente."""
        response = self.client.get(reverse('accounts:signup'))
        self.assertEqual(response.status_code, 200)

    def test_signup_valid_data_creates_user(self):
        """Registro con datos válidos crea usuario y redirige."""
        response = self.client.post(reverse('accounts:signup'), {
            'nombre':    'María',
            'apellido':  'González',
            'email':     'maria@test.com',
            'telefono':  '809-555-1234',
            'cedula':    '001-0000001-1',
            'edad':      '28',
            'municipio': str(self.municipio.id),
            'password':  'SecurePass99',
        })
        self.assertRedirects(response, '/ciudadano/dashboard/', fetch_redirect_response=False)
        self.assertTrue(Usuario.objects.filter(email='maria@test.com').exists())

    def test_signup_duplicate_email_rejected(self):
        """Registro con email ya existente devuelve error y no duplica usuario."""
        Usuario.objects.create_user(email='dup@test.com', password='pass', nombre='Dup')
        count_before = Usuario.objects.count()
        response = self.client.post(reverse('accounts:signup'), {
            'nombre': 'X', 'apellido': 'Y',
            'email': 'dup@test.com', 'password': 'AnotherPass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Usuario.objects.count(), count_before)

    def test_signup_invalid_email_format(self):
        """Registro con email inválido muestra error."""
        response = self.client.post(reverse('accounts:signup'), {
            'nombre': 'Pedro', 'apellido': 'Test',
            'email': 'not-an-email', 'password': 'ValidPass123',
        })
        self.assertEqual(response.status_code, 200)

    def test_signup_short_password_rejected(self):
        """Contraseña < 8 caracteres muestra error."""
        response = self.client.post(reverse('accounts:signup'), {
            'nombre': 'Ana', 'apellido': 'Test',
            'email': 'ana@test.com', 'password': 'short',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Usuario.objects.filter(email='ana@test.com').exists())

    def test_signup_missing_nombre(self):
        """Registro sin nombre devuelve error."""
        response = self.client.post(reverse('accounts:signup'), {
            'nombre': '', 'apellido': 'Test',
            'email': 'noname@test.com', 'password': 'ValidPass123',
        })
        self.assertEqual(response.status_code, 200)

    # ── Logout ────────────────────────────────────────────────────
    def test_logout_post_redirects_home(self):
        """POST a logout redirige al inicio."""
        self.client.login(username='test@limpiord.com', password='TestPass123!')
        response = self.client.post(reverse('accounts:logout'))
        self.assertRedirects(response, '/', fetch_redirect_response=False)

    def test_logout_clears_session(self):
        """Después del logout, el usuario ya no está autenticado."""
        self.client.login(username='test@limpiord.com', password='TestPass123!')
        self.client.post(reverse('accounts:logout'))
        response = self.client.get(reverse('accounts:login'))
        # Si el usuario está deslogueado, no redirige
        self.assertEqual(response.status_code, 200)


class UsuarioModelTests(TestCase):
    """Tests del modelo de usuario."""

    def test_create_user_stores_email_and_role(self):
        user = Usuario.objects.create_user(
            email='model@test.com',
            password='pass12345',
            nombre='Test',
            rol=Usuario.ROL_CIUDADANO,
        )
        self.assertEqual(user.email, 'model@test.com')
        self.assertEqual(user.rol, Usuario.ROL_CIUDADANO)
        self.assertTrue(user.check_password('pass12345'))

    def test_user_is_not_staff_by_default(self):
        user = Usuario.objects.create_user(
            email='nostaff@test.com',
            password='pass12345',
            nombre='NoStaff',
        )
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_user_email_is_username(self):
        """El campo USERNAME_FIELD debe ser email."""
        self.assertEqual(Usuario.USERNAME_FIELD, 'email')
