import requests
import zipfile
import io
import os
import json
from datetime import datetime

import pandas as pd


# CONFIGURACIÓN
URL = "https://www.kaggle.com/api/v1/datasets/download/vijayuv/onlineretail"

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "OnlineRetail.csv")
AUDIT_PATH = os.path.join(DATA_DIR, "auditoria_extraccion.json")


# DESCARGA DESDE KAGGLE
def descargar_dataset():

    os.makedirs(DATA_DIR, exist_ok=True)

    print("Descargando dataset desde Kaggle...")

    response = requests.get(URL)

    if response.status_code != 200:
        raise Exception(
            f"Error al descargar el dataset. Código: {response.status_code}"
        )

    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:

        csv_files = [
            archivo
            for archivo in zip_file.namelist()
            if archivo.lower().endswith(".csv")
        ]

        if not csv_files:
            raise Exception("No se encontró ningún archivo CSV.")

        csv_file = csv_files[0]

        with zip_file.open(csv_file) as file:
            df = pd.read_csv(file, encoding="latin1")

    df.to_csv(CSV_PATH, index=False)

    print(f"Dataset guardado en: {CSV_PATH}")

    return df, csv_file


# CARGAR DATASET LOCAL
def cargar_dataset():

    if os.path.exists(CSV_PATH):

        print("El dataset ya existe localmente.")
        print("No se realizará una nueva descarga.")

        df = pd.read_csv(CSV_PATH, encoding="latin1")

        return df, "OnlineRetail.csv"

    return descargar_dataset()


# AUDITORÍA
def generar_auditoria(df, archivo, descargado):

    auditoria = {
        "fecha_extraccion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fuente": "Kaggle",
        "dataset": "vijayuv/onlineretail",
        "metodo": "API pública de Kaggle",
        "url_api": URL,
        "archivo": archivo,
        "registros": len(df),
        "columnas": len(df.columns),
        "nombres_columnas": df.columns.tolist(),
        "descarga_realizada": descargado,
        "estado": "EXITOSO"
    }

    with open(AUDIT_PATH, "w", encoding="utf-8") as archivo_json:
        json.dump(auditoria, archivo_json, indent=4, ensure_ascii=False)

    print(f"\nAuditoría guardada en: {AUDIT_PATH}")


# PROCESO PRINCIPAL

if __name__ == "__main__":

    descargado = not os.path.exists(CSV_PATH)

    df, archivo = cargar_dataset()

    print("\n--- INFORMACIÓN DEL DATASET ---")
    print("Registros:", len(df))
    print("Columnas:", len(df.columns))
    print("Columnas:", df.columns.tolist())

    print("\nPrimeros registros:")
    print(df.head())

    generar_auditoria(
        df,
        archivo,
        descargado
    )