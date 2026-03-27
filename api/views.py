# api/views.py
from rest_framework import viewsets, permissions
from reportes.models import Reporte
from .serializers import ReporteSerializer, PerfilSerializer
from reportes.services import ReporteService
from rest_framework.response import Response
from rest_framework.decorators import action

class ReporteViewSet(viewsets.ModelViewSet):
    """Endpoints para la app móvil ciudadana o integraciones externas."""
    serializer_class = ReporteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reporte.objects.filter(ciudadano=self.request.user)

    def perform_create(self, serializer):
        # Usar el Service de negocio en lugar del save() directo
        # Así encapsulamos creación, puntos y notificación
        ReporteService.crear_reporte(
            datos=serializer.validated_data,
            usuario=self.request.user
        )

class CiudadanoViewSet(viewsets.ViewSet):
    """Endpoints para info del panel del ciudadano en la app móvil."""
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def perfil(self, request):
        perfil = request.user.perfil_gamificacion
        serializer = PerfilSerializer(perfil)
        return Response(serializer.data)
