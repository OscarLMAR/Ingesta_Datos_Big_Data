import sqlite3
import os
import pandas as pd
import json
from datetime import datetime


# CONFIGURACIÓN

DATA_DIR = "data"
CSV_PATH = os.path.join(DATA_DIR, "OnlineRetail.csv")
DB_PATH = os.path.join(DATA_DIR, "retail.db")
AUDIT_PATH = os.path.join(DATA_DIR, "auditoria_carga.json")


# CONEXIÓN

def conectar():

    os.makedirs(DATA_DIR, exist_ok=True)

    return sqlite3.connect(DB_PATH)


# CARGA DE DATOS EN SQLITE

def cargar_datos():

    print("Leyendo OnlineRetail.csv...")

    df = pd.read_csv(
        CSV_PATH,
        encoding="latin1"
    )

    registros_origen = len(df)

    print(f"Registros leídos desde CSV: {registros_origen}")

    conexion = conectar()

    print("Creando tabla de staging...")

    df.to_sql(
        "stg_online_retail",
        conexion,
        if_exists="replace",
        index=False
    )

    cursor = conexion.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM stg_online_retail"
    )

    registros_sqlite = cursor.fetchone()[0]

    diferencia = registros_origen - registros_sqlite

    conexion.close()

    print("\n--- RESULTADO DE LA CARGA ---")
    print(f"Registros origen:  {registros_origen}")
    print(f"Registros SQLite:  {registros_sqlite}")
    print(f"Diferencia:        {diferencia}")

    return registros_origen, registros_sqlite, diferencia


# AUDITORÍA

def generar_auditoria(
    registros_origen,
    registros_sqlite,
    diferencia
):

    auditoria = {
        "fecha_carga": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "archivo_origen": "OnlineRetail.csv",
        "base_destino": "retail.db",
        "tabla_destino": "stg_online_retail",
        "registros_origen": registros_origen,
        "registros_sqlite": registros_sqlite,
        "diferencia": diferencia,
        "estado": (
            "EXITOSO"
            if diferencia == 0
            else "CON DIFERENCIAS"
        )
    }

    with open(
        AUDIT_PATH,
        "w",
        encoding="utf-8"
    ) as archivo:

        json.dump(
            auditoria,
            archivo,
            indent=4,
            ensure_ascii=False
        )

    print(
        f"\nAuditoría guardada en: {AUDIT_PATH}"
    )



if __name__ == "__main__":

    registros_origen, registros_sqlite, diferencia = cargar_datos()

    generar_auditoria(
        registros_origen,
        registros_sqlite,
        diferencia
    )