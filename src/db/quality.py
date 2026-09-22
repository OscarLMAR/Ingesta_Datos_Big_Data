import sqlite3
import os
import json
from datetime import datetime


# CONFIGURACIÓN
DB_PATH = os.path.join("data", "retail.db")
AUDIT_PATH = os.path.join("data", "auditoria_calidad.json")


# AUDITORÍA DE CALIDAD
def auditar_calidad():

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    auditoria = {
        "fecha_auditoria": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    }

    # Total de registros
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
    """)

    total = cursor.fetchone()[0]

    auditoria["total_registros"] = total

    # Registros con CustomerID nulo
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE CustomerID IS NULL
    """)

    auditoria["customer_id_nulos"] = cursor.fetchone()[0]

    # Registros con Description nula
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE Description IS NULL
    """)

    auditoria["description_nulos"] = cursor.fetchone()[0]

    # Cantidades <= 0
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE Quantity <= 0
    """)

    auditoria["cantidad_no_positiva"] = cursor.fetchone()[0]

    # Precios <= 0
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE UnitPrice <= 0
    """)

    auditoria["precio_no_positivo"] = cursor.fetchone()[0]

    # Facturas canceladas
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE InvoiceNo LIKE 'C%'
    """)

    auditoria["facturas_canceladas"] = cursor.fetchone()[0]

    # Registros duplicados
    cursor.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT
                InvoiceNo,
                StockCode,
                Description,
                Quantity,
                InvoiceDate,
                UnitPrice,
                CustomerID,
                Country,
                COUNT(*) AS cantidad
            FROM stg_online_retail
            GROUP BY
                InvoiceNo,
                StockCode,
                Description,
                Quantity,
                InvoiceDate,
                UnitPrice,
                CustomerID,
                Country
            HAVING COUNT(*) > 1
        )
    """)

    auditoria["grupos_duplicados"] = cursor.fetchone()[0]

    conexion.close()

    # AUDITORÍA
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

    # RESULTADOS

    print("\n--- AUDITORÍA DE CALIDAD ---")

    for clave, valor in auditoria.items():
        print(f"{clave}: {valor}")

    print(
        f"\nAuditoría guardada en: {AUDIT_PATH}"
    )


# EJECUCIÓN

if __name__ == "__main__":
    auditar_calidad()