# core/views.py
from django.shortcuts import render

def landing_page(request):
    """Página de inicio pública de LimpioRD."""
    return render(request, 'core/landing.html')
