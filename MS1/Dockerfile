FROM python:3.10-slim

WORKDIR /app

# Copiar e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el script principal
COPY main.py .

# Ejecutar el proceso de ingesta
CMD ["python", "main.py"]
