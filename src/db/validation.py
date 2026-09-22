import sqlite3
import os


DB_PATH = os.path.join("data", "retail.db")


def validar_reglas():

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()

    print("\n--- VALIDACIÓN DE REGLAS DE LIMPIEZA ---")

    # Total original
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
    """)

    total = cursor.fetchone()[0]

    # Ventas no canceladas
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE InvoiceNo NOT LIKE 'C%'
    """)

    no_canceladas = cursor.fetchone()[0]

    # Cantidad positiva
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE Quantity > 0
    """)

    cantidad_valida = cursor.fetchone()[0]

    # Precio positivo
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE UnitPrice > 0
    """)

    precio_valido = cursor.fetchone()[0]

    # Regla combinada
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE InvoiceNo NOT LIKE 'C%'
          AND Quantity > 0
          AND UnitPrice > 0
    """)

    registros_validos = cursor.fetchone()[0]

    # Regla combinada + cliente
    cursor.execute("""
        SELECT COUNT(*)
        FROM stg_online_retail
        WHERE InvoiceNo NOT LIKE 'C%'
          AND Quantity > 0
          AND UnitPrice > 0
          AND CustomerID IS NOT NULL
    """)

    ventas_con_cliente = cursor.fetchone()[0]

    conexion.close()

    print(f"Total original:                 {total}")
    print(f"No canceladas:                  {no_canceladas}")
    print(f"Cantidad positiva:              {cantidad_valida}")
    print(f"Precio positivo:                {precio_valido}")
    print(f"Cumplen reglas principales:     {registros_validos}")
    print(f"Cumplen reglas + cliente:       {ventas_con_cliente}")

    print("\n--- REGISTROS QUE NO CUMPLEN ---")

    print(
        f"Registros excluidos por reglas principales: "
        f"{total - registros_validos}"
    )

    print(
        f"Registros válidos finales para ventas: "
        f"{registros_validos}"
    )


if __name__ == "__main__":
    validar_reglas()