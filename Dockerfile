# 1. USAR PYTHON 3.11 (Compatible con Torch)
FROM python:3.11-slim

# 2. INSTALAR LIBRERÍAS DE SISTEMA CRUCIALES
# Esto soluciona los errores de compilación 'subprocess-exited-with-error' y 'exit code: 1'
RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    apt-get update -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false && \
    apt-get install -y --no-install-recommends --fix-missing \
    build-essential \
    pkg-config \
    libjpeg-dev \
    libpng-dev \
    zlib1g-dev \
    libatlas-base-dev \
    libsm6 \
    libxext6 \
    libglib2.0-0 \
    libcairo2-dev && \
    rm -rf /var/lib/apt/lists/*

# 3. DEFINIR EL DIRECTORIO DE TRABAJO
WORKDIR /usr/src/app

# 4. INSTALAR DEPENDENCIAS DE PYTHON
# Copiar requirements.txt primero (mejor uso de caché de Docker)
COPY requirements.txt .

# Ejecutar la instalación de Python con las dependencias de sistema listas
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5. COPIAR EL CÓDIGO RESTANTE
COPY . .

# 6. EXPONER EL PUERTO (opcional pero recomendado)
EXPOSE 10000

# 7. COMANDO DE INICIO (El Start Command en Render)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]