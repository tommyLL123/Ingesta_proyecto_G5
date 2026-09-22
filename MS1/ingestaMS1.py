import os
import pandas as pd
import sqlalchemy
import boto3

# Configuración MySQL
DB_USER = os.getenv("DB_USER", "ms1_user")
DB_PASS = os.getenv("DB_PASS", "ms1_password")
DB_HOST = os.getenv("DB_HOST", "172.31.77.26")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "ms1_clientes_db")

# Configuración S3
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "proyecto-cloud-bucket-g5")
FOLDER_PREFIX = "MS1"

def ingesta_ms1():
    engine = sqlalchemy.create_engine(
        f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    s3_client = boto3.client("s3")

    tablas = ["clientes", "pedidos", "pedido_detalle"]

    for tabla in tablas:
        print(f"[MS1] Extrayendo data de la tabla: {tabla}...")

        df = pd.read_sql(
            f"SELECT * FROM {tabla};",
            con=engine
        )

        print(f"[MS1] {tabla}: {len(df)} registros extraídos")

        local_csv = f"{tabla}.csv"
        df.to_csv(local_csv, index=False)

        s3_key = f"{FOLDER_PREFIX}/{local_csv}"

        print(f"[AWS S3] Subiendo a s3://{S3_BUCKET}/{s3_key}...")
        s3_client.upload_file(
            local_csv,
            S3_BUCKET,
            s3_key
        )

        if os.path.exists(local_csv):
            os.remove(local_csv)

    print("[MS1] Ingesta completada correctamente.")

if __name__ == "__main__":
    ingesta_ms1()
