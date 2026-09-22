import os
import pandas as pd
from pymongo import MongoClient
from bson import ObjectId
import boto3

# Configuración MongoDB
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://ms3_user:ms3_password@172.31.77.26:27017/?authSource=admin"
)

DB_NAME = os.getenv("DB_NAME", "ms3_reservas_db")

# Configuración S3
S3_BUCKET = os.getenv(
    "S3_BUCKET_NAME",
    "proyecto-cloud-bucket-g5"
)

FOLDER_PREFIX = "MS3"


def ingesta_ms3():

    # Conexión MongoDB
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Verificar conexión
    client.admin.command("ping")
    print("[MS3] Conexión a MongoDB correcta.")

    db = client[DB_NAME]

    # Cliente S3
    s3_client = boto3.client("s3")

    colecciones = [
        "mesas",
        "reservas"
    ]

    for col in colecciones:

        print(f"[MS3] Extrayendo colección: {col}...")

        # Traer todos los documentos
        docs = list(db[col].find({}))

        print(f"[MS3] {col}: {len(docs)} documentos extraídos")

        # Convertir a DataFrame
        df = pd.DataFrame(docs)

        # Convertir ObjectId de MongoDB a texto para poder guardarlo en CSV
        if not df.empty:
            for columna in df.columns:
                df[columna] = df[columna].apply(
                    lambda valor: str(valor)
                    if isinstance(valor, ObjectId)
                    else valor
                )

        # Crear CSV
        local_csv = f"{col}.csv"
        df.to_csv(local_csv, index=False)

        # Ruta en S3
        s3_key = f"{FOLDER_PREFIX}/{local_csv}"

        print(
            f"[AWS S3] Subiendo a "
            f"s3://{S3_BUCKET}/{s3_key}..."
        )

        s3_client.upload_file(
            local_csv,
            S3_BUCKET,
            s3_key
        )

        # Eliminar CSV local
        if os.path.exists(local_csv):
            os.remove(local_csv)

    client.close()

    print("[MS3] Ingesta completada correctamente.")


if __name__ == "__main__":
    ingesta_ms3()
