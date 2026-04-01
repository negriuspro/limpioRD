#!/bin/bash
set -e

echo "==> Creando directorios necesarios..."
mkdir -p logs media staticfiles static

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

echo "==> Cargando datos iniciales..."
# Verificar si ya existen usuarios para evitar duplicados
USERS=$(python manage.py shell -c "from accounts.models import Usuario; print(Usuario.objects.count())" 2>/dev/null || echo "0")

if [ "$USERS" = "0" ]; then
    echo "    Buscando fixture en fixtures/datos_iniciales.json..."
    if [ -f "fixtures/datos_iniciales.json" ]; then
        python manage.py loaddata fixtures/datos_iniciales.json \
            && echo "    Datos cargados correctamente." \
            || echo "    Advertencia: no se pudieron cargar los datos iniciales."
    else
        echo "    Advertencia: No se encontró fixtures/datos_iniciales.json"
    fi
else
    echo "    (Omitido: la BD ya tiene $USERS usuario(s))"
fi

echo "==> Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo ""
echo "  =============================================="
echo "  LimpioRD listo en http://localhost:8000"
echo "  =============================================="
echo ""

exec python manage.py runserver 0.0.0.0:8000
