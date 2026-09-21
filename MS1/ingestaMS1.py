import os
import pandas as pd
import sqlalchemy
import boto3

# Configuración por variables de entorno
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "172.17.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "bd_ms1")

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "proyecto-bucket-g5")
FOLDER_PREFIX = "MS1"  # Carpeta dentro del S3

def ingesta_ms1():
    # Conexión
    engine = sqlalchemy.create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    s3_client = boto3.client('s3')

    # Tablas a extraer (PULL 100%)
    tablas = ["clientes", "pedido_detalle"]

    for tabla in tablas:
        print(f"[MS1] Extrayendo data de la tabla: {tabla}...")
        
        # 1. Extracción total
        df = pd.read_sql(f"SELECT * FROM {tabla};", con=engine)
        
        # 2. Generación de CSV local estático
        local_csv = f"{tabla}.csv"
        df.to_csv(local_csv, index=False)

        # 3. Ruta exacta en S3: MS1/clientes.csv
        s3_key = f"{FOLDER_PREFIX}/{local_csv}"
        
        print(f"[AWS S3] Subiendo a s3://{S3_BUCKET}/{s3_key}...")
        s3_client.upload_file(local_csv, S3_BUCKET, s3_key)
        
        # Limpieza local
        if os.path.exists(local_csv):
            os.remove(local_csv)

if __name__ == "__main__":
    ingesta_ms1()
