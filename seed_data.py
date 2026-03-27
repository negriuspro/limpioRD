import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limpiord.settings.base')
django.setup()

from reportes.models import CategoriaResiduo
from ayuntamientos.models import Municipio
from negocios.models import Producto, Proveedor

def seed():
    # 1. Municipios
    muns = [
        ("Distrito Nacional", "DN", 18.4861, -69.9312),
        ("Santo Domingo Este", "SDE", 18.4884, -69.8519),
        ("Santo Domingo Oeste", "SDO", 18.4900, -70.0100),
        ("Santiago de los Caballeros", "STGO", 19.4517, -70.6970),
    ]
    for nom, cod, lat, lng in muns:
        Municipio.objects.get_or_create(
            nombre=nom, 
            defaults={'codigo': cod, 'latitud_centro': lat, 'longitud_centro': lng}
        )
    print(f"Created {len(muns)} municipios.")

    # 2. Categorias
    cats = [
        ("Plásticos", "trash"),
        ("Orgánicos", "apple-box"),
        ("Escombros", "truck"),
        ("Electrónicos", "cpu-chip"),
    ]
    for nom, ico in cats:
        CategoriaResiduo.objects.get_or_create(nombre=nom, defaults={'icono': ico})
    print(f"Created {len(cats)} categorias.")

    # 3. Datos de Negocio (para el dashboard financiero)
    prov, _ = Proveedor.objects.get_or_create(nombre="Distribuidora Dominicana", defaults={'contacto': '829-555-0199'})
    p1, _ = Producto.objects.get_or_create(
        nombre="Bolsas Biodegradables X10", 
        defaults={'precio': 150.00, 'stock': 50, 'proveedor': prov, 'categoria': 'Limpieza', 'stock_minimo': 5}
    )
    p2, _ = Producto.objects.get_or_create(
        nombre="Botella de Agua Reutilizable", 
        defaults={'precio': 450.00, 'stock': 12, 'proveedor': prov, 'categoria': 'Accesorios', 'stock_minimo': 3}
    )
    print("Seed data completed.")

if __name__ == "__main__":
    seed()
