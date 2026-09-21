import os
import pandas as pd
import sqlalchemy
import boto3

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_HOST = os.getenv("DB_HOST", "172.17.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bd_ms2")

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "proyecto-bucket-g5")
FOLDER_PREFIX = "MS2"

def ingesta_ms2():
    engine = sqlalchemy.create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    s3_client = boto3.client('s3')

    tablas = ["ms2_categorias", "ms2_platos", "ms2_resenas"]

    for tabla in tablas:
        print(f"[MS2] Extrayendo data de la tabla: {tabla}...")
        
        df = pd.read_sql(f"SELECT * FROM {tabla};", con=engine)
        
        local_csv = f"{tabla}.csv"
        df.to_csv(local_csv, index=False)

        # Ruta exacta en S3: MS2/ms2_categorias.csv, etc.
        s3_key = f"{FOLDER_PREFIX}/{local_csv}"
        
        print(f"[AWS S3] Subiendo a s3://{S3_BUCKET}/{s3_key}...")
        s3_client.upload_file(local_csv, S3_BUCKET, s3_key)
        
        if os.path.exists(local_csv):
            os.remove(local_csv)

if __name__ == "__main__":
    ingesta_ms2()
