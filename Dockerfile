FROM python:3.12-slim

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libuuid1 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar todos los archivos al contenedor
COPY . .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto
EXPOSE 8000

# Comando por defecto para iniciar el servidor
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
