# Usar Python 3.11, que es compatible con Torch 2.1.2
FROM python:3.11-slim 

# Establecer el directorio de trabajo
WORKDIR /usr/src/app

# Copiar e instalar dependencias. Render usará este comando.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar tu código
COPY . .

# Comando de inicio para FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "10000"]