# 1. Usar Python 3.11 (Compatible con Torch)
FROM python:3.11-slim

# 2. INSTALAR LIBRERÍAS DE SISTEMA (SOLUCIÓN al "subprocess-exited-with-error")
# 'build-essential' incluye el compilador C/C++.
# 'libcairo2-dev' es crucial para pycairo/cairosvg.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libcairo2-dev \
        pkg-config && \
    rm -rf /var/lib/apt/lists/*

# 3. DEFINIR EL DIRECTORIO DE TRABAJO
WORKDIR /usr/src/app

# 4. INSTALAR DEPENDENCIAS DE PYTHON
COPY requirements.txt .
# Ahora 'pip install' funcionará porque las herramientas necesarias ya existen.
RUN pip install --no-cache-dir -r requirements.txt

# 5. COPIAR EL CÓDIGO RESTANTE
COPY . .

# 6. COMANDO DE INICIO
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]