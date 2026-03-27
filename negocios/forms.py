# negocios/forms.py
from django import forms
from .models import Venta, Gasto, Producto, Cliente

class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descripcion', 'monto', 'fecha_gasto', 'categoria', 'estado']
        widgets = {
            'fecha_gasto': forms.DateInput(attrs={'type': 'date', 'class': 'rounded-xl border-gray-200'}),
            'monto': forms.NumberInput(attrs={'class': 'rounded-xl border-gray-200'}),
            'descripcion': forms.TextInput(attrs={'class': 'rounded-xl border-gray-200'}),
            'categoria': forms.TextInput(attrs={'class': 'rounded-xl border-gray-200'}),
        }

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['cliente', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'rounded-xl border-gray-200 bg-white'}),
            'estado': forms.Select(attrs={'class': 'rounded-xl border-gray-200 bg-white'}),
        }
