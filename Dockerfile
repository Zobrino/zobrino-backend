FROM python:3.12-slim

# Instala libuuid y otras dependencias del sistema necesarias
RUN apt-get update && apt-get install -y libuuid1 libsndfile1 ffmpeg curl && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo
WORKDIR /app

# Copia todos los archivos del proyecto
COPY . .

# Instala dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Comando para ejecutar la app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
