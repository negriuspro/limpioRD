# core/views.py
from django.shortcuts import render


def landing_page(request):
    """Página de inicio pública de LimpioRD."""
    from reportes.models import Reporte
    from accounts.models import Usuario
    from ayuntamientos.models import Municipio

    stats = {
        'reportes_resueltos': Reporte.objects.filter(estado=Reporte.ESTADO_RESUELTO).count(),
        'ciudadanos_activos': Usuario.objects.filter(rol='ciudadano', esta_activo=True).count(),
        'municipios_activos': Municipio.objects.filter(esta_activo=True).count(),
    }
    return render(request, 'core/landing.html', {'stats': stats})
