# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ReporteViewSet, CiudadanoViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'reportes', ReporteViewSet, basename='reporte')
router.register(r'ciudadano', CiudadanoViewSet, basename='ciudadano')

urlpatterns = [
    path('v1/', include(router.urls)),
    
    # Endpoints JWT para login en aplicación móvil
    path('auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
