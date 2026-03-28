import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'limpiord.settings.development')
django.setup()

from reportes.models import CategoriaResiduo, Reporte
from ayuntamientos.models import Municipio
from negocios.models import Producto, Proveedor
from accounts.models import Usuario


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
    print(f"OK {len(muns)} municipios")

    # 2. Categorias
    cats = [
        ("Plástico",     "trash",    "#3b82f6"),
        ("Orgánico",     "apple-box","#22c55e"),
        ("Escombros",    "truck",    "#f97316"),
        ("Electrónico",  "cpu-chip", "#8b5cf6"),
        ("Vidrio",       "glass",    "#06b6d4"),
        ("Papel/Cartón", "file",     "#eab308"),
        ("Peligroso",    "warning",  "#ef4444"),
    ]
    for nom, ico, color in cats:
        CategoriaResiduo.objects.get_or_create(
            nombre=nom, defaults={'icono': ico, 'color': color}
        )
    print(f"OK {len(cats)} categorias")

    # 3. Negocios seed
    prov, _ = Proveedor.objects.get_or_create(
        nombre="Distribuidora Dominicana",
        defaults={'contacto': '829-555-0199'}
    )
    Producto.objects.get_or_create(
        nombre="Bolsas Biodegradables X10",
        defaults={'precio': 150.00, 'stock': 50, 'proveedor': prov, 'categoria': 'Limpieza', 'stock_minimo': 5}
    )
    Producto.objects.get_or_create(
        nombre="Botella de Agua Reutilizable",
        defaults={'precio': 450.00, 'stock': 12, 'proveedor': prov, 'categoria': 'Accesorios', 'stock_minimo': 3}
    )
    print("OK Productos de negocio")

    # 4. Actualizar reportes existentes sin barrio
    dn = Municipio.objects.filter(codigo='DN').first()
    if not dn:
        print("ERROR: Municipio DN no encontrado, omitiendo fix de barrios")
        return

    barrios_dn = [
        ("Gazcue",           18.4720, -69.9290),
        ("Villa Consuelo",   18.4780, -69.9050),
        ("Naco",             18.4850, -69.9460),
        ("Piantini",         18.4730, -69.9500),
        ("Bella Vista",      18.4680, -69.9540),
        ("Los Mameyes",      18.5100, -69.8700),
        ("Cristo Rey",       18.4900, -69.9650),
        ("La Julia",         18.4800, -69.9700),
        ("Ensanche Ozama",   18.5050, -69.8850),
        ("Villa Juana",      18.4750, -69.9180),
        ("Km 9",             18.5200, -69.8600),
        ("Los Jardines",     18.4820, -69.9350),
        ("Simón Bolívar",    18.4760, -69.9420),
        ("Gualey",           18.4830, -69.9230),
    ]

    sin_barrio = Reporte.objects.filter(barrio='')
    updated = 0
    for r in sin_barrio:
        nombre, lat, lng = random.choice(barrios_dn)
        r.barrio = nombre
        r.latitud = lat + random.uniform(-0.003, 0.003)
        r.longitud = lng + random.uniform(-0.003, 0.003)
        if not r.municipio_id:
            r.municipio = dn
        r.save(update_fields=['barrio', 'latitud', 'longitud', 'municipio'])
        updated += 1

    print(f"OK {updated} reportes actualizados con barrio y coordenadas")
    print("Seed completo.")


if __name__ == "__main__":
    seed()
