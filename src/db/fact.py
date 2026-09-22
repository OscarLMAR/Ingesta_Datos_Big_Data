import sqlite3
import os
import pandas as pd


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


def crear_fact_ventas():

    conexion = sqlite3.connect(DB_PATH)

    print("Creando FactVentas...")

    # 1. Leer ventas limpias

    ventas = pd.read_sql_query(
        """
        SELECT
            InvoiceNo,
            StockCode,
            InvoiceDate,
            CustomerID,
            Quantity,
            UnitPrice
        FROM ventas_limpias
        """,
        conexion
    )

    print("Ventas cargadas:", len(ventas))

    # 2. Normalizar InvoiceDate

    ventas["Fecha"] = pd.to_datetime(
        ventas["InvoiceDate"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # 3. Obtener dimensiones

    dim_fecha = pd.read_sql_query(
        """
        SELECT
            DateID,
            Fecha
        FROM DimFecha
        """,
        conexion
    )

    dim_cliente = pd.read_sql_query(
        """
        SELECT
            ClienteID,
            CustomerID
        FROM DimCliente
        """,
        conexion
    )

    dim_producto = pd.read_sql_query(
        """
        SELECT
            ProductoID,
            StockCode
        FROM DimProducto
        """,
        conexion
    )

    # 4. Relacionar con DimFecha

    ventas = ventas.merge(
        dim_fecha,
        on="Fecha",
        how="inner"
    )

    # 5. Relacionar con DimProducto

    ventas = ventas.merge(
        dim_producto,
        on="StockCode",
        how="inner"
    )

    # 6. Relacionar con DimCliente
    #    LEFT JOIN porque CustomerID puede ser nulo

    ventas = ventas.merge(
        dim_cliente,
        on="CustomerID",
        how="left"
    )

    # 7. Calcular TotalVenta

    ventas["TotalVenta"] = (
        ventas["Quantity"] *
        ventas["UnitPrice"]
    )

    # 8. Seleccionar estructura final

    fact = ventas[
        [
            "InvoiceNo",
            "DateID",
            "ClienteID",
            "ProductoID",
            "Quantity",
            "UnitPrice",
            "TotalVenta"
        ]
    ].copy()

    # 9. Crear FactVentas

    conexion.execute(
        "DROP TABLE IF EXISTS FactVentas"
    )

    fact.to_sql(
        "FactVentas",
        conexion,
        if_exists="replace",
        index_label="FactVentaID"
    )

    conexion.commit()

    # 10. Validaciones

    total_limpias = conexion.execute(
        """
        SELECT COUNT(*)
        FROM ventas_limpias
        """
    ).fetchone()[0]

    total_fact = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        """
    ).fetchone()[0]

    diferencia = total_limpias - total_fact

    ventas_sin_cliente = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        WHERE ClienteID IS NULL
        """
    ).fetchone()[0]

    ventas_sin_producto = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        WHERE ProductoID IS NULL
        """
    ).fetchone()[0]

    ventas_sin_fecha = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        WHERE DateID IS NULL
        """
    ).fetchone()[0]

    total_ventas = conexion.execute(
        """
        SELECT SUM(TotalVenta)
        FROM FactVentas
        """
    ).fetchone()[0]

    conexion.close()

    print("\n--- FACTVENTAS ---")
    print("Registros ventas_limpias:", total_limpias)
    print("Registros FactVentas:    ", total_fact)
    print("Diferencia:               ", diferencia)

    print("\n--- INTEGRIDAD ---")
    print("Ventas sin cliente:", ventas_sin_cliente)
    print("Ventas sin producto:", ventas_sin_producto)
    print("Ventas sin fecha:", ventas_sin_fecha)

    print("\n--- MÉTRICA ---")
    print(
        "Valor total de ventas:",
        round(total_ventas, 2)
    )


if __name__ == "__main__":
    crear_fact_ventas()