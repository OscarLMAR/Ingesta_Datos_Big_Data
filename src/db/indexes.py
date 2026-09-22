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


def crear_indices():

    conexion = sqlite3.connect(DB_PATH)

    print("Creando índices...")

    indices = [

        """
        CREATE INDEX IF NOT EXISTS idx_factventas_date
        ON FactVentas(DateID)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_factventas_cliente
        ON FactVentas(ClienteID)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_factventas_producto
        ON FactVentas(ProductoID)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_factventas_invoice
        ON FactVentas(InvoiceNo)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_dimcliente_customer
        ON DimCliente(CustomerID)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_dimproducto_stock
        ON DimProducto(StockCode)
        """,

        """
        CREATE INDEX IF NOT EXISTS idx_dimfecha_fecha
        ON DimFecha(Fecha)
        """
    ]

    for indice in indices:
        conexion.execute(indice)

    conexion.commit()

    print("\n--- ÍNDICES CREADOS ---")

    resultado = conexion.execute(
        """
        SELECT
            name,
            tbl_name
        FROM sqlite_master
        WHERE type = 'index'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY tbl_name, name
        """
    ).fetchall()

    for nombre, tabla in resultado:
        print(f"{nombre} → {tabla}")

    conexion.close()


if __name__ == "__main__":
    crear_indices()