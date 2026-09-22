import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

DB_PATH = BASE_DIR / "data" / "retail.db"
AUDITORIA_EXTRACCION = BASE_DIR / "data" / "auditoria_extraccion.json"
OUTPUT_PATH = BASE_DIR /"src" / "static" / "auditoria" / "ingestion.txt"


def obtener_registros_extraidos():
    with open(AUDITORIA_EXTRACCION, "r", encoding="utf-8") as archivo:
        auditoria = json.load(archivo)

    return auditoria["registros"]


def obtener_registros_bd(conn, tabla):
    query = f"SELECT COUNT(*) FROM {tabla}"
    resultado = conn.execute(query).fetchone()

    return resultado[0]


def generar_auditoria():
    print("    AUDITORÍA FINAL DE INGESTA")

    # Crear directorio de salida
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Registros reportados por la extracción
    registros_api = obtener_registros_extraidos()

    # Conexión a SQLite
    conn = sqlite3.connect(DB_PATH)

    try:
        # Registros almacenados en staging
        registros_staging = obtener_registros_bd(
            conn,
            "stg_online_retail"
        )

        # Registros válidos del proceso de transformación
        registros_limpios = obtener_registros_bd(
            conn,
            "ventas_limpias"
        )

        # Registros almacenados en la tabla de hechos
        registros_fact = obtener_registros_bd(
            conn,
            "FactVentas"
        )

        # Diferencias
        diferencia_api_bd = registros_api - registros_staging
        diferencia_limpios_fact = registros_limpios - registros_fact

        # Estado de la ingesta
        ingesta_ok = diferencia_api_bd == 0

        # Estado del modelo final
        modelo_ok = diferencia_limpios_fact == 0

        estado_final = "APROBADO" if ingesta_ok and modelo_ok else "REVISAR"

        # Generar contenido del archivo
        contenido = f"""
        
AUDITORÍA DE INGESTA DE DATOS

Fuente:
Kaggle - Online Retail

Método de extracción:
API pública de Kaggle

Archivo de origen:
OnlineRetail.csv


COMPARACIÓN API VS SQLITE

Registros extraídos desde el API:
{registros_api}

Registros almacenados en SQLite:
{registros_staging}

Diferencia:
{diferencia_api_bd}

Estado de la ingesta:
{"OK" if ingesta_ok else "REVISAR"}


PROCESAMIENTO DE DATOS

Registros originales:
{registros_staging}

Registros válidos después de las reglas:
{registros_limpios}

Registros excluidos:
{registros_staging - registros_limpios}


VALIDACIÓN FACTVENTAS

Registros válidos:
{registros_limpios}

Registros almacenados en FactVentas:
{registros_fact}

Diferencia:
{diferencia_limpios_fact}

Estado:
{"OK" if modelo_ok else "REVISAR"}


RESULTADO FINAL

Estado de la auditoría:
{estado_final}

La comparación entre los registros extraídos
y los registros almacenados en SQLite
permite verificar la integridad de la ingesta.

FIN DE LA AUDITORÍA
""".strip()

        # Guardar archivo
        with open(OUTPUT_PATH, "w", encoding="utf-8") as archivo:
            archivo.write(contenido)

        # Mostrar resultado en consola
        print("\n--- COMPARACIÓN API VS SQLITE ---")
        print(f"Registros API:       {registros_api}")
        print(f"Registros SQLite:    {registros_staging}")
        print(f"Diferencia:          {diferencia_api_bd}")

        print("\n--- FACTVENTAS ---")
        print(f"Registros válidos:   {registros_limpios}")
        print(f"Registros FactVentas:{registros_fact}")
        print(f"Diferencia:          {diferencia_limpios_fact}")

        print("\n--- RESULTADO ---")
        print(f"Estado:              {estado_final}")

        print(f"\nAuditoría guardada en:")
        print(OUTPUT_PATH)

    finally:
        conn.close()


if __name__ == "__main__":
    generar_auditoria() 