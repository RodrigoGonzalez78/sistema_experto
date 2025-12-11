# ============================================
# Sistema Experto Epidemiológico - Dockerfile
# ============================================

# Imagen base Python 3.10 (compatibilidad con fasthtml y experta)
FROM python:3.10-slim

# Metadatos
LABEL maintainer="Sistema Experto"
LABEL description="Sistema de diagnóstico Dengue vs COVID-19"
LABEL version="1.0"

# Evitar prompts interactivos
ENV DEBIAN_FRONTEND=noninteractive

# Variables de entorno Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python + parche para frozendict (Python 3.10+ compatibility)
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -c "import collections; collections.Mapping = collections.abc.Mapping" || true \
    && sed -i 's/collections.Mapping/collections.abc.Mapping/g' /usr/local/lib/python3.10/site-packages/frozendict/__init__.py 2>/dev/null || true

# Copiar código de la aplicación
COPY app/ ./app/

# Crear directorio para datos persistentes
RUN mkdir -p /app/data

# Puerto expuesto
EXPOSE 5001

# Comando de ejecución
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5001"]
