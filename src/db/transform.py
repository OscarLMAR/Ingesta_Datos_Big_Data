import sqlite3
import os


DB_PATH = os.path.join("data", "retail.db")


def crear_ventas_limpias():

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    print("Creando tabla ventas_limpias...")

    cursor.execute("""
        DROP TABLE IF EXISTS ventas_limpias
    """)

    cursor.execute("""
        CREATE TABLE ventas_limpias AS
        SELECT *
        FROM stg_online_retail
        WHERE InvoiceNo NOT LIKE 'C%'
          AND Quantity > 0
          AND UnitPrice > 0
    """)

    cursor.execute("""
        SELECT COUNT(*)
        FROM ventas_limpias
    """)

    total_limpio = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
    """)

    total_origen = cursor.fetchone()[0]

    conexion.commit()
    conexion.close()

    print("\n--- RESULTADO DE LA TRANSFORMACIÓN ---")
    print(f"Registros originales: {total_origen}")
    print(f"Registros válidos:    {total_limpio}")
    print(f"Registros excluidos:  {total_origen - total_limpio}")


if __name__ == "__main__":
    crear_ventas_limpias()