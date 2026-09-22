import sqlite3
import os


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

DB_PATH = os.path.join(
    BASE_DIR,
    "data",
    "retail.db"
)


def validar_modelo():

    conexion = sqlite3.connect(DB_PATH)

    print("VALIDACIÓN FINAL DEL MODELO ESTRELLA")

    # 1. Conteo de tablas
    tablas = [
        "stg_online_retail",
        "ventas_limpias",
        "DimFecha",
        "DimCliente",
        "DimProducto",
        "FactVentas"
    ]

    print("\n--- TABLAS ---")

    for tabla in tablas:

        existe = conexion.execute(
            """
            SELECT COUNT(*)
            FROM sqlite_master
            WHERE type = 'table'
              AND name = ?
            """,
            (tabla,)
        ).fetchone()[0]

        if existe:
            total = conexion.execute(
                f"SELECT COUNT(*) FROM {tabla}"
            ).fetchone()[0]

            print(f"{tabla}: {total:,} registros")

        else:
            print(f"{tabla}: NO EXISTE")

    # 2. Integridad de fechas
    fechas_invalidas = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas f
        LEFT JOIN DimFecha d
            ON f.DateID = d.DateID
        WHERE d.DateID IS NULL
        """
    ).fetchone()[0]

    # 3. Integridad de productos
    productos_invalidos = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas f
        LEFT JOIN DimProducto p
            ON f.ProductoID = p.ProductoID
        WHERE p.ProductoID IS NULL
        """
    ).fetchone()[0]

    # 4. Integridad de clientes
    clientes_invalidos = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas f
        LEFT JOIN DimCliente c
            ON f.ClienteID = c.ClienteID
        WHERE f.ClienteID IS NOT NULL
          AND c.ClienteID IS NULL
        """
    ).fetchone()[0]

    print("\n--- INTEGRIDAD REFERENCIAL ---")

    print(
        "FactVentas con DateID inválido:",
        fechas_invalidas
    )

    print(
        "FactVentas con ProductoID inválido:",
        productos_invalidos
    )

    print(
        "FactVentas con ClienteID inválido:",
        clientes_invalidos
    )

    # 5. Reglas de calidad

    cantidades_invalidas = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        WHERE Quantity <= 0
        """
    ).fetchone()[0]

    precios_invalidos = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        WHERE UnitPrice <= 0
        """
    ).fetchone()[0]

    canceladas = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        WHERE InvoiceNo LIKE 'C%'
        """
    ).fetchone()[0]

    totalventa_incorrecta = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        WHERE ABS(
            TotalVenta - (Quantity * UnitPrice)
        ) > 0.000001
        """
    ).fetchone()[0]

    print("\n--- REGLAS DE CALIDAD ---")

    print(
        "Cantidades <= 0:",
        cantidades_invalidas
    )

    print(
        "Precios <= 0:",
        precios_invalidos
    )

    print(
        "Facturas canceladas:",
        canceladas
    )

    print(
        "TotalVenta incorrecto:",
        totalventa_incorrecta
    )

    # 6. Total económico
    total_ventas = conexion.execute(
        """
        SELECT SUM(TotalVenta)
        FROM FactVentas
        """
    ).fetchone()[0]

    print("\n--- MÉTRICAS ---")

    print(
        "Valor total de ventas:",
        round(total_ventas, 2)
    )

    conexion.close()


if __name__ == "__main__":
    validar_modelo()