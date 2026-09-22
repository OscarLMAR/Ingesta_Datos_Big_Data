import sqlite3
import os
import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "data", "retail.db")


def crear_dim_fecha():

    conexion = sqlite3.connect(DB_PATH)

    print("Creando DimFecha...")

    df = pd.read_sql_query(
        """
        SELECT InvoiceDate
        FROM ventas_limpias
        """,
        conexion
    )

    df["Fecha"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    df = df.dropna(subset=["Fecha"])

    df["Fecha"] = df["Fecha"].dt.normalize()

    df = df[["Fecha"]].drop_duplicates()

    df = df.sort_values("Fecha").reset_index(drop=True)

    df.insert(
        0,
        "DateID",
        range(1, len(df) + 1)
    )

    df["Año"] = df["Fecha"].dt.year
    df["Mes"] = df["Fecha"].dt.month
    df["Dia"] = df["Fecha"].dt.day

    df["Fecha"] = df["Fecha"].dt.strftime("%Y-%m-%d")

    df = df[
        [
            "DateID",
            "Fecha",
            "Año",
            "Mes",
            "Dia"
        ]
    ]

    df.to_sql(
        "DimFecha",
        conexion,
        if_exists="replace",
        index=False
    )

    total = pd.read_sql_query(
        "SELECT COUNT(*) AS total FROM DimFecha",
        conexion
    ).iloc[0]["total"]

    minimo = pd.read_sql_query(
        "SELECT MIN(Fecha) AS fecha FROM DimFecha",
        conexion
    ).iloc[0]["fecha"]

    maximo = pd.read_sql_query(
        "SELECT MAX(Fecha) AS fecha FROM DimFecha",
        conexion
    ).iloc[0]["fecha"]

    conexion.close()

    print("\n--- DIMFECHA ---")
    print("Registros:", total)
    print("Fecha mínima:", minimo)
    print("Fecha máxima:", maximo)


def crear_dim_cliente():

    conexion = sqlite3.connect(DB_PATH)

    print("\nCreando DimCliente...")

    df = pd.read_sql_query(
        """
        SELECT
            CustomerID,
            MIN(Country) AS Country
        FROM ventas_limpias
        WHERE CustomerID IS NOT NULL
        GROUP BY CustomerID
        """,
        conexion
    )

    # Ordenar para generar un identificador estable
    df = df.sort_values(
        by=["CustomerID", "Country"]
    ).reset_index(drop=True)

    # Crear identificador de dimensión
    df.insert(
        0,
        "ClienteID",
        range(1, len(df) + 1)
    )

    df = df[
        [
            "ClienteID",
            "CustomerID",
            "Country"
        ]
    ]

    df.to_sql(
        "DimCliente",
        conexion,
        if_exists="replace",
        index=False
    )

    total = pd.read_sql_query(
        "SELECT COUNT(*) AS total FROM DimCliente",
        conexion
    ).iloc[0]["total"]

    clientes_unicos = pd.read_sql_query(
        """
        SELECT COUNT(DISTINCT CustomerID) AS total
        FROM ventas_limpias
        WHERE CustomerID IS NOT NULL
        """,
        conexion
    ).iloc[0]["total"]

    conexion.close()

    print("\n--- DIMCLIENTE ---")
    print("Registros en DimCliente:", total)
    print("CustomerID únicos:", clientes_unicos)

def crear_dim_producto():

    conexion = sqlite3.connect(DB_PATH)

    print("\nCreando DimProducto...")

    df = pd.read_sql_query(
        """
        SELECT
            StockCode,
            MAX(Description) AS Description
        FROM ventas_limpias
        WHERE StockCode IS NOT NULL
        GROUP BY StockCode
        """,
        conexion
    )

    # Ordenar productos
    df = df.sort_values(
        by="StockCode"
    ).reset_index(drop=True)

    # Crear identificador de dimensión
    df.insert(
        0,
        "ProductoID",
        range(1, len(df) + 1)
    )

    df = df[
        [
            "ProductoID",
            "StockCode",
            "Description"
        ]
    ]

    df.to_sql(
        "DimProducto",
        conexion,
        if_exists="replace",
        index=False
    )

    total = pd.read_sql_query(
        """
        SELECT COUNT(*) AS total
        FROM DimProducto
        """,
        conexion
    ).iloc[0]["total"]

    productos_unicos = pd.read_sql_query(
        """
        SELECT COUNT(DISTINCT StockCode) AS total
        FROM ventas_limpias
        WHERE StockCode IS NOT NULL
        """,
        conexion
    ).iloc[0]["total"]

    descripciones_nulas = pd.read_sql_query(
        """
        SELECT COUNT(*) AS total
        FROM DimProducto
        WHERE Description IS NULL
        """,
        conexion
    ).iloc[0]["total"]

    conexion.close()

    print("\n--- DIMPRODUCTO ---")
    print("Registros en DimProducto:", total)
    print("StockCode únicos:", productos_unicos)
    print("Descripciones nulas:", descripciones_nulas)

if __name__ == "__main__":
    crear_dim_fecha()
    crear_dim_cliente()
    crear_dim_producto()