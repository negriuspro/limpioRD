# reportes/forms.py
from django import forms
from .models import Reporte, CategoriaResiduo
from ayuntamientos.models import Municipio

class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['municipio', 'categoria', 'descripcion', 'barrio', 'referencia', 'latitud', 'longitud', 'foto']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe el problema...', 'class': 'rounded-2xl border-gray-200 w-full'}),
            'barrio': forms.TextInput(attrs={'placeholder': 'Ej: Los Prados', 'class': 'rounded-xl border-gray-200 w-full'}),
            'referencia': forms.TextInput(attrs={'placeholder': 'Ej: Frente al parque...', 'class': 'rounded-xl border-gray-200 w-full'}),
            'latitud': forms.HiddenInput(),
            'longitud': forms.HiddenInput(),
        }

    def clean_latitud(self):
        lat = self.cleaned_data.get('latitud')
        if not lat:
            raise forms.ValidationError("La ubicación es obligatoria.")
        return lat

    def clean_longitud(self):
        lon = self.cleaned_data.get('longitud')
        if not lon:
            raise forms.ValidationError("La ubicación es obligatoria.")
        return lon
