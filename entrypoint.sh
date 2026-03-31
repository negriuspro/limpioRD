#!/bin/sh
set -e

echo "==> Creando directorios necesarios..."
mkdir -p logs media staticfiles static

echo "==> Aplicando migraciones..."
python manage.py migrate --noinput

echo "==> Cargando datos iniciales..."
USERS=$(python manage.py shell -c "from accounts.models import Usuario; print(Usuario.objects.count())" 2>/dev/null || echo "0")
if [ "$USERS" = "0" ]; then
    python manage.py loaddata fixtures/datos_iniciales.json \
        && echo "    Datos cargados correctamente." \
        || echo "    Advertencia: no se pudieron cargar los datos iniciales."
else
    echo "    (Omitido: la BD ya tiene $USERS usuario(s))"
fi

echo "==> Recopilando archivos estáticos..."
python manage.py collectstatic --noinput --clear

echo ""
echo "  LimpioRD listo en http://localhost:8000"
echo ""
exec python manage.py runserver 0.0.0.0:8000
