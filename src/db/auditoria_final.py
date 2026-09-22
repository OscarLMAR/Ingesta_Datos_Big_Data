import sqlite3
import os
import json
from datetime import datetime


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

AUDIT_PATH = os.path.join(
    BASE_DIR,
    "data",
    "auditoria_final.json"
)


def ejecutar_auditoria():

    conexion = sqlite3.connect(DB_PATH)

    print("    AUDITORÍA FINAL DEL PROYECTO")

    conteos = {}

    tablas = [
        "stg_online_retail",
        "ventas_limpias",
        "DimFecha",
        "DimCliente",
        "DimProducto",
        "FactVentas"
    ]

    for tabla in tablas:

        total = conexion.execute(
            f"SELECT COUNT(*) FROM {tabla}"
        ).fetchone()[0]

        conteos[tabla] = total

    # Registros descartados
    registros_originales = conteos["stg_online_retail"]
    registros_validos = conteos["ventas_limpias"]

    registros_excluidos = (
        registros_originales -
        registros_validos
    )

    ventas_sin_cliente = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas
        WHERE ClienteID IS NULL
        """
    ).fetchone()[0]

    ventas_con_cliente = (
        conteos["FactVentas"] -
        ventas_sin_cliente
    )

    
    fecha_invalidas = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas f
        LEFT JOIN DimFecha d
            ON f.DateID = d.DateID
        WHERE d.DateID IS NULL
        """
    ).fetchone()[0]

    producto_invalidos = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas f
        LEFT JOIN DimProducto p
            ON f.ProductoID = p.ProductoID
        WHERE p.ProductoID IS NULL
        """
    ).fetchone()[0]

    cliente_invalidos = conexion.execute(
        """
        SELECT COUNT(*)
        FROM FactVentas f
        LEFT JOIN DimCliente c
            ON f.ClienteID = c.ClienteID
        WHERE f.ClienteID IS NOT NULL
          AND c.ClienteID IS NULL
        """
    ).fetchone()[0]

    # Reglas de calidad
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

    # Métricas
    total_ventas = conexion.execute(
        """
        SELECT SUM(TotalVenta)
        FROM FactVentas
        """
    ).fetchone()[0]

    unidades_vendidas = conexion.execute(
        """
        SELECT SUM(Quantity)
        FROM FactVentas
        """
    ).fetchone()[0]

    # Índices
    indices = conexion.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'index'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    ).fetchall()

    indices = [
        indice[0]
        for indice in indices
    ]

    # Estado final
    errores = (
        fecha_invalidas +
        producto_invalidos +
        cliente_invalidos +
        cantidades_invalidas +
        precios_invalidos +
        canceladas +
        totalventa_incorrecta
    )

    estado = "APROBADO" if errores == 0 else "REVISAR"

    auditoria = {

        "fecha_auditoria": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        "estado": estado,

        "registros": {
            "originales": registros_originales,
            "validos": registros_validos,
            "excluidos": registros_excluidos,
            "fact_ventas": conteos["FactVentas"]
        },

        "dimensiones": {
            "DimFecha": conteos["DimFecha"],
            "DimCliente": conteos["DimCliente"],
            "DimProducto": conteos["DimProducto"]
        },

        "clientes": {
            "con_cliente": ventas_con_cliente,
            "sin_cliente": ventas_sin_cliente
        },

        "integridad_referencial": {
            "fechas_invalidas": fecha_invalidas,
            "productos_invalidos": producto_invalidos,
            "clientes_invalidos": cliente_invalidos
        },

        "calidad": {
            "cantidades_invalidas": cantidades_invalidas,
            "precios_invalidos": precios_invalidos,
            "facturas_canceladas": canceladas,
            "total_venta_incorrecto": totalventa_incorrecta
        },

        "metricas": {
            "valor_total_ventas": round(total_ventas, 2),
            "unidades_vendidas": unidades_vendidas
        },

        "indices": indices
    }

    # Auditoría
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

    conexion.close()

    # Mostra de resumen
    print("\n--- REGISTROS ---")
    print("Originales:", registros_originales)
    print("Válidos:", registros_validos)
    print("Excluidos:", registros_excluidos)
    print("FactVentas:", conteos["FactVentas"])

    print("\n--- DIMENSIONES ---")
    print("DimFecha:", conteos["DimFecha"])
    print("DimCliente:", conteos["DimCliente"])
    print("DimProducto:", conteos["DimProducto"])

    print("\n--- CLIENTES ---")
    print("Con cliente:", ventas_con_cliente)
    print("Sin cliente:", ventas_sin_cliente)

    print("\n--- INTEGRIDAD ---")
    print("Fechas inválidas:", fecha_invalidas)
    print("Productos inválidos:", producto_invalidos)
    print("Clientes inválidos:", cliente_invalidos)

    print("\n--- CALIDAD ---")
    print("Cantidades inválidas:", cantidades_invalidas)
    print("Precios inválidos:", precios_invalidos)
    print("Facturas canceladas:", canceladas)
    print("TotalVenta incorrecto:", totalventa_incorrecta)

    print("\n--- MÉTRICAS ---")
    print("Valor total ventas:", round(total_ventas, 2))
    print("Unidades vendidas:", unidades_vendidas)

    print("\n--- ESTADO FINAL ---")
    print("Estado:", estado)

    print("\nAuditoría guardada en:")
    print(AUDIT_PATH)


if __name__ == "__main__":
    ejecutar_auditoria()