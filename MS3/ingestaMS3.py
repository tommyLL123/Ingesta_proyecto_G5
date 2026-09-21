import os
import pandas as pd
from pymongo import MongoClient
import boto3

MONGO_URI = os.getenv("MONGO_URI", "mongodb://root:password@172.17.0.1:27017/")
DB_NAME = os.getenv("DB_NAME", "bd_ms3")

S3_BUCKET = os.getenv("S3_BUCKET_NAME", "proyecto-bucket-g5")
FOLDER_PREFIX = "MS3"

def ingesta_ms3():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    s3_client = boto3.client('s3')

    colecciones = ["mesas", "reservas"]

    for col in colecciones:
        print(f"[MS3] Extrayendo colección: {col}...")
        
        # 1. Traer todos los documentos omitiendo el id autogenerado de Mongo
        docs = list(db[col].find({}, {'_id': 0}))
        
        # 2. Convertir a DataFrame y guardar como CSV
        df = pd.DataFrame(docs)
        local_csv = f"{col}.csv"
        df.to_csv(local_csv, index=False)

        # 3. Ruta exacta en S3: MS3/mesas.csv
        s3_key = f"{FOLDER_PREFIX}/{local_csv}"
        
        print(f"[AWS S3] Subiendo a s3://{S3_BUCKET}/{s3_key}...")
        s3_client.upload_file(local_csv, S3_BUCKET, s3_key)
        
        if os.path.exists(local_csv):
            os.remove(local_csv)

if __name__ == "__main__":
    ingesta_ms3()
