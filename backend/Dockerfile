# Usa una imagen base oficial de Python
FROM python:3.10-slim

# Instala las dependencias del sistema necesarias para Neo4j y Python
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Define el directorio de trabajo en el contenedor
WORKDIR /app

# Copia solo el archivo requirements.txt
COPY requirements.txt .

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto de los archivos del proyecto al contenedor
COPY . .

# Expone el puerto en el que corre Flask (5000 por defecto)
EXPOSE 5000

# Comando para ejecutar la aplicación
CMD ["python", "app/server.py"]
