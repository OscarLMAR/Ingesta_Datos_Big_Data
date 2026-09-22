import sqlite3
from pathlib import Path
import pandas as pd


# Configuración de rutas
BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "data" / "retail.db"

OUTPUT_DIR = BASE_DIR / "src" / "xlsx"
AUDIT_DIR = BASE_DIR / "src" / "static" / "auditoria"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
AUDIT_DIR.mkdir(parents=True, exist_ok=True)

CLEANED_PATH = OUTPUT_DIR / "cleaned_data.csv"
AUDIT_PATH = AUDIT_DIR / "cleaning_report.txt"


# Funciones Auxiliares
# Para calcular los límites IQR y la cantidad de valores extremos.
def calcular_outliers_iqr(df, columna):
    q1 = df[columna].quantile(0.25)
    q3 = df[columna].quantile(0.75)

    iqr = q3 - q1

    limite_inferior = q1 - 1.5 * iqr
    limite_superior = q3 + 1.5 * iqr

    outliers = (
        (df[columna] < limite_inferior)
        | (df[columna] > limite_superior)
    ).sum()

    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "limite_inferior": limite_inferior,
        "limite_superior": limite_superior,
        "outliers": int(outliers),
    }


# Extracción de SQLite
print("=" * 60)
print("EA2 - PREPROCESAMIENTO Y LIMPIEZA DE DATOS")
print("=" * 60)

print("\n[1/6] Extrayendo datos desde SQLite...")

connection = sqlite3.connect(DB_PATH)

df = pd.read_sql_query(
    "SELECT * FROM stg_online_retail",
    connection
)

connection.close()

registros_iniciales = len(df)

print(f"Registros extraídos: {registros_iniciales}")
print(f"Columnas: {len(df.columns)}")


# Análisis inicial
print("\n[2/6] Analizando calidad inicial...")

duplicados_iniciales = int(df.duplicated().sum())

nulos_description_inicial = int(df["Description"].isna().sum())
nulos_customer_inicial = int(df["CustomerID"].isna().sum())

cantidad_no_positiva = int((df["Quantity"] <= 0).sum())
precio_no_positivo = int((df["UnitPrice"] <= 0).sum())

canceladas = int(
    df["InvoiceNo"]
    .astype(str)
    .str.startswith("C")
    .sum()
)

fechas_invalidas = int(
    pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    ).isna().sum()
)

outliers_quantity = calcular_outliers_iqr(
    df,
    "Quantity"
)

outliers_unitprice = calcular_outliers_iqr(
    df,
    "UnitPrice"
)


# Corrección de tipos y estandarización
print("\n[3/6] Corrigiendo tipos y estandarizando datos...")

# Campos de texto
for columna in [
    "InvoiceNo",
    "StockCode",
    "Description",
    "Country"
]:
    df[columna] = df[columna].astype("string").str.strip()

# Descripción nula
df["Description"] = df["Description"].fillna(
    "SIN DESCRIPCION"
)

# Fecha
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"],
    errors="coerce"
)

# CustomerID como entero nullable
df["CustomerID"] = pd.to_numeric(
    df["CustomerID"],
    errors="coerce"
).astype("Int64")

# Tipos numéricos
df["Quantity"] = pd.to_numeric(
    df["Quantity"],
    errors="coerce"
).astype("Int64")

df["UnitPrice"] = pd.to_numeric(
    df["UnitPrice"],
    errors="coerce"
)


# Elominación de registros no válidos
print("\n[4/6] Aplicando reglas de limpieza...")

antes_limpieza = len(df)

# Duplicados exactos
df = df.drop_duplicates()

despues_duplicados = len(df)

# Cantidades no válidas
df = df[df["Quantity"] > 0]

despues_quantity = len(df)

# Precios no válidos
df = df[df["UnitPrice"] > 0]

despues_precio = len(df)

# Fechas inválidas
df = df[df["InvoiceDate"].notna()]

despues_fecha = len(df)


registros_eliminados = antes_limpieza - len(df)


# Transformaciones
print("\n[5/6] Aplicando transformaciones adicionales...")

# Estandarización del país
df["Country"] = df["Country"].str.strip()

# Creación de medida derivada de venta
df["TotalVenta"] = (
    df["Quantity"].astype("float64")
    * df["UnitPrice"]
)

# Ordena cronológicamente
df = df.sort_values(
    by=["InvoiceDate", "InvoiceNo", "StockCode"]
).reset_index(drop=True)


# Exportación de resultados
print("\n[6/6] Generando evidencias...")

# Muestra representativa de 100 registros
muestra = df.head(100)

muestra.to_csv(
    CLEANED_PATH,
    index=False,
    encoding="utf-8-sig"
)

# Estado final
registros_finales = len(df)

duplicados_finales = int(df.duplicated().sum())

nulos_description_final = int(
    df["Description"].isna().sum()
)

fechas_invalidas_final = int(
    df["InvoiceDate"].isna().sum()
)

cantidad_no_positiva_final = int(
    (df["Quantity"] <= 0).sum()
)

precio_no_positivo_final = int(
    (df["UnitPrice"] <= 0).sum()
)


# Auditoría
with open(AUDIT_PATH, "w", encoding="utf-8") as archivo:

    archivo.write(
        "============================================================\n"
    )
    archivo.write(
        "EA2 - AUDITORÍA DE PREPROCESAMIENTO Y LIMPIEZA\n"
    )
    archivo.write(
        "============================================================\n\n"
    )

    archivo.write("1. FUENTE DE DATOS\n")
    archivo.write("------------------\n")
    archivo.write(f"Base de datos: {DB_PATH}\n")
    archivo.write("Tabla origen: stg_online_retail\n\n")

    archivo.write("2. ESTADO INICIAL\n")
    archivo.write("-----------------\n")
    archivo.write(
        f"Registros iniciales: {registros_iniciales}\n"
    )
    archivo.write(
        f"Duplicados exactos: {duplicados_iniciales}\n"
    )
    archivo.write(
        f"Description nulo: {nulos_description_inicial}\n"
    )
    archivo.write(
        f"CustomerID nulo: {nulos_customer_inicial}\n"
    )
    archivo.write(
        f"Quantity <= 0: {cantidad_no_positiva}\n"
    )
    archivo.write(
        f"UnitPrice <= 0: {precio_no_positivo}\n"
    )
    archivo.write(
        f"Facturas canceladas: {canceladas}\n"
    )
    archivo.write(
        f"Fechas inválidas: {fechas_invalidas}\n"
    )
    archivo.write(
        f"Outliers Quantity (IQR): "
        f"{outliers_quantity['outliers']}\n"
    )
    archivo.write(
        f"Outliers UnitPrice (IQR): "
        f"{outliers_unitprice['outliers']}\n\n"
    )

    archivo.write("3. OPERACIONES REALIZADAS\n")
    archivo.write("-------------------------\n")
    archivo.write(
        "1. Eliminación de duplicados exactos.\n"
    )
    archivo.write(
        "2. Eliminación de registros con Quantity <= 0.\n"
    )
    archivo.write(
        "3. Eliminación de registros con UnitPrice <= 0.\n"
    )
    archivo.write(
        "4. Conversión de InvoiceDate a datetime.\n"
    )
    archivo.write(
        "5. Conversión de CustomerID a entero nullable.\n"
    )
    archivo.write(
        "6. Conversión de campos numéricos a tipos apropiados.\n"
    )
    archivo.write(
        "7. Imputación de Description nulo con "
        "'SIN DESCRIPCION'.\n"
    )
    archivo.write(
        "8. Estandarización de espacios en campos de texto.\n"
    )
    archivo.write(
        "9. Creación de la variable TotalVenta.\n"
    )
    archivo.write(
        "10. Ordenamiento cronológico de los registros.\n\n"
    )

    archivo.write("4. TRATAMIENTO DE OUTLIERS\n")
    archivo.write("-------------------------\n")
    archivo.write(
        "Se utilizó el método del rango intercuartílico (IQR)\n"
        "para detectar valores estadísticamente extremos.\n\n"
    )

    archivo.write(
        f"Quantity - Q1: {outliers_quantity['q1']}\n"
    )
    archivo.write(
        f"Quantity - Q3: {outliers_quantity['q3']}\n"
    )
    archivo.write(
        f"Quantity - IQR: {outliers_quantity['iqr']}\n"
    )
    archivo.write(
        f"Quantity - límite superior: "
        f"{outliers_quantity['limite_superior']}\n"
    )
    archivo.write(
        f"Quantity - outliers: "
        f"{outliers_quantity['outliers']}\n\n"
    )

    archivo.write(
        f"UnitPrice - Q1: {outliers_unitprice['q1']}\n"
    )
    archivo.write(
        f"UnitPrice - Q3: {outliers_unitprice['q3']}\n"
    )
    archivo.write(
        f"UnitPrice - IQR: {outliers_unitprice['iqr']}\n"
    )
    archivo.write(
        f"UnitPrice - límite superior: "
        f"{outliers_unitprice['limite_superior']}\n"
    )
    archivo.write(
        f"UnitPrice - outliers: "
        f"{outliers_unitprice['outliers']}\n\n"
    )

    archivo.write(
        "Los outliers fueron identificados y documentados, "
        "pero no eliminados automáticamente debido a que un "
        "valor extremo no implica necesariamente un error de "
        "calidad. Se conservaron para evitar eliminar "
        "transacciones potencialmente válidas.\n\n"
    )

    archivo.write("5. IMPACTO DE LA LIMPIEZA\n")
    archivo.write("------------------------\n")
    archivo.write(
        f"Registros antes: {registros_iniciales}\n"
    )
    archivo.write(
        f"Registros después: {registros_finales}\n"
    )
    archivo.write(
        f"Registros eliminados: {registros_eliminados}\n"
    )

    archivo.write(
        f"Reducción porcentual: "
        f"{(registros_eliminados / registros_iniciales) * 100:.2f}%\n\n"
    )

    archivo.write("6. ESTADO FINAL\n")
    archivo.write("---------------\n")
    archivo.write(
        f"Duplicados finales: {duplicados_finales}\n"
    )
    archivo.write(
        f"Description nulo final: {nulos_description_final}\n"
    )
    archivo.write(
        f"Fechas inválidas finales: {fechas_invalidas_final}\n"
    )
    archivo.write(
        f"Quantity <= 0 final: {cantidad_no_positiva_final}\n"
    )
    archivo.write(
        f"UnitPrice <= 0 final: {precio_no_positivo_final}\n"
    )
    archivo.write(
        f"Registros en muestra CSV: {len(muestra)}\n"
    )
    archivo.write(
        f"Columnas en resultado: {len(df.columns)}\n\n"
    )

    archivo.write("7. RESULTADO\n")
    archivo.write("------------\n")

    if (
        duplicados_finales == 0
        and cantidad_no_positiva_final == 0
        and precio_no_positivo_final == 0
        and fechas_invalidas_final == 0
    ):
        archivo.write(
            "ESTADO: APROBADO\n"
        )
        archivo.write(
            "El conjunto de datos cumple las reglas "
            "principales de limpieza definidas para la EA2.\n"
        )
    else:
        archivo.write(
            "ESTADO: REVISAR\n"
        )


print("\n" + "=" * 60)
print("PROCESO DE LIMPIEZA FINALIZADO")
print("=" * 60)

print(f"Registros iniciales: {registros_iniciales}")
print(f"Registros finales:   {registros_finales}")
print(f"Eliminados:          {registros_eliminados}")
print(
    f"Reducción:           "
    f"{(registros_eliminados / registros_iniciales) * 100:.2f}%"
)

print(f"\nMuestra generada: {CLEANED_PATH}")
print(f"Auditoría generada: {AUDIT_PATH}")