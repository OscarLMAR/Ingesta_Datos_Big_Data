import sqlite3
import pandas as pd
from pathlib import Path


# Rutas del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "retail.db"
OUTPUT_PATH = BASE_DIR / "data" / "muestra_ingestion.csv"


def generar_muestra():
    print("   GENERACIÓN DE MUESTRA CON PANDAS")

    print(f"\nBase de datos: {DB_PATH}")

    # Conexión a SQLite
    conn = sqlite3.connect(DB_PATH)

    try:
        # Seleccionar una muestra de registros de FactVentas
        query = """
        SELECT
            FactVentaID,
            InvoiceNo,
            DateID,
            ClienteID,
            ProductoID,
            Quantity,
            UnitPrice,
            TotalVenta
        FROM FactVentas
        LIMIT 100
        """

        df = pd.read_sql_query(query, conn)

        # Crear directorio de salida si no existe
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Exportar muestra a CSV
        df.to_csv(
            OUTPUT_PATH,
            index=False,
            encoding="utf-8-sig"
        )

        print("\n--- RESULTADO ---")
        print(f"Registros de la muestra: {len(df)}")
        print(f"Columnas: {len(df.columns)}")
        print(f"Archivo generado: {OUTPUT_PATH}")

        print("\n--- MUESTRA ---")
        print(df.head())

        print("\nEstado: OK")

    finally:
        conn.close()


if __name__ == "__main__":
    generar_muestra()