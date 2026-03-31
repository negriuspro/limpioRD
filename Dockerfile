FROM python:3.12-slim

# libmagic para python-magic en Linux
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmagic1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Directorios que Django necesita
RUN mkdir -p logs media staticfiles static

EXPOSE 8000

ENTRYPOINT ["sh", "entrypoint.sh"]
