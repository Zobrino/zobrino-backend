FROM python:3.12-slim

# Instalar librerías necesarias del sistema
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    libuuid1 \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar todos los archivos del proyecto al contenedor
COPY . .

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto que usará uvicorn
EXPOSE 8000

# Comando para iniciar el servidor FastAPI
CMD ["uvicorn", "main:app", "--host=0.0.0.0", "--port=8000"]
