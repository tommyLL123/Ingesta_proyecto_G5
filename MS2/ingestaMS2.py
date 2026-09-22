import os
import pandas as pd
import sqlalchemy
import boto3

# Configuración PostgreSQL
DB_USER = os.getenv("DB_USER", "ms2_user")
DB_PASS = os.getenv("DB_PASS", "ms2_password")
DB_HOST = os.getenv("DB_HOST", "172.31.77.26")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "ms2_menu_db")

# Configuración S3
S3_BUCKET = os.getenv("S3_BUCKET_NAME", "proyecto-cloud-bucket-g5")
FOLDER_PREFIX = "MS2"


def ingesta_ms2():

    # Conexión PostgreSQL
    engine = sqlalchemy.create_engine(
        f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    # Cliente S3
    s3_client = boto3.client("s3")

    # Tablas de MS2
    tablas = [
        "categorias",
        "platos",
        "resenas"
    ]

    for tabla in tablas:

        print(f"[MS2] Extrayendo data de la tabla: {tabla}...")

        # Extracción completa
        df = pd.read_sql(
            f"SELECT * FROM public.{tabla};",
            con=engine
        )

        print(f"[MS2] {tabla}: {len(df)} registros extraídos")

        # Generar CSV
        local_csv = f"{tabla}.csv"
        df.to_csv(local_csv, index=False)

        # Ruta S3
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

    engine.dispose()

    print("[MS2] Ingesta completada correctamente.")


if __name__ == "__main__":
    ingesta_ms2()
