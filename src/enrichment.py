import json
from pathlib import Path
import xml.etree.ElementTree as ET

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
BASE_DATA_PATH = BASE_DIR / "src" / "xlsx" / "cleaned_data.csv"
SOURCES_DIR = BASE_DIR / "data" / "fuentes_enriquecimiento"
OUTPUT_DIR = BASE_DIR / "src" / "xlsx"
AUDIT_DIR = BASE_DIR / "src" / "static" / "auditoria"
XLSX_SOURCE = SOURCES_DIR / "inventory_source.xlsx"
XLSX_SEED = SOURCES_DIR / "inventory_source.csv"
OUTPUT_PATH = OUTPUT_DIR / "enriched_data.csv"
AUDIT_PATH = AUDIT_DIR / "enrichment_report.txt"


def cargar_fuentes():
    """Lee los archivos que se van a utilizar para enriquecer los datos."""
    json_path = SOURCES_DIR / "product_catalog.json"
    with json_path.open(encoding="utf-8") as source_file:
        product_catalog = pd.DataFrame(json.load(source_file))

    if not XLSX_SOURCE.exists():
        inventory_seed = pd.read_csv(XLSX_SEED)
        inventory_seed.to_excel(XLSX_SOURCE, index=False)

    inventory = pd.read_excel(XLSX_SOURCE)
    country_info = pd.read_csv(SOURCES_DIR / "country_info.csv")

    xml_root = ET.parse(SOURCES_DIR / "shipping.xml").getroot()
    shipping = pd.DataFrame(
        [{field.tag: field.text for field in country} for country in xml_root.findall("country")]
    )

    customer_segments = pd.read_html(
        (SOURCES_DIR / "customer_segments.html").as_uri()
    )[0]
    promotions = pd.read_csv(SOURCES_DIR / "promotions.txt", sep="|")

    return product_catalog, inventory, country_info, shipping, customer_segments, promotions


def normalizar_columna(data, columna):
    data[columna] = data[columna].astype(str).str.strip().str.upper()
    return data


def agregar_fuente(base, fuente, columna, nombre):
    """Agrega una fuente a la base usando una unión por la columna indicada."""
    base = normalizar_columna(base, columna)
    fuente = normalizar_columna(fuente, columna)
    fuente = fuente.drop_duplicates(subset=columna)

    columnas_nuevas = [col for col in fuente.columns if col != columna]
    fuente = fuente.rename(
        columns={col: f"{col}_{nombre}" for col in columnas_nuevas}
    )
    return base.merge(fuente, on=columna, how="left")


def escribir_auditoria(base, enriquecido):
    with AUDIT_PATH.open("w", encoding="utf-8") as report:
        report.write("EA3 - AUDITORIA DE ENRIQUECIMIENTO DE DATOS\n")
        report.write("=============================================\n\n")
        report.write(f"Archivo utilizado: {BASE_DATA_PATH}\n")
        report.write(f"Registros iniciales: {len(base)}\n")
        report.write(f"Registros finales: {len(enriquecido)}\n")
        report.write(f"Columnas iniciales: {len(base.columns)}\n")
        report.write(f"Columnas finales: {len(enriquecido.columns)}\n\n")
        report.write("Fuentes utilizadas:\n")
        report.write("- product_catalog.json\n")
        report.write("- inventory_source.xlsx\n")
        report.write("- country_info.csv\n")
        report.write("- shipping.xml\n")
        report.write("- customer_segments.html\n")
        report.write("- promotions.txt\n\n")
        report.write("Se limpiaron las claves y se hicieron uniones left join.\n")
        report.write("Los registros duplicados de las fuentes fueron eliminados.\n")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(BASE_DATA_PATH)
    product_catalog, inventory, country_info, shipping, customer_segments, promotions = cargar_fuentes()

    enriched = agregar_fuente(base, product_catalog, "StockCode", "catalogo")
    enriched = agregar_fuente(enriched, inventory, "StockCode", "inventario")
    enriched = agregar_fuente(enriched, country_info, "Country", "pais")
    enriched = agregar_fuente(enriched, shipping, "Country", "envio")
    enriched = agregar_fuente(enriched, customer_segments, "CustomerID", "cliente")
    enriched = agregar_fuente(enriched, promotions, "StockCode", "promociones")

    enriched.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    escribir_auditoria(base, enriched)
    print(f"Enriquecimiento completado: {len(enriched)} registros, {len(enriched.columns)} columnas")
    print(f"Salida: {OUTPUT_PATH}")
    print(f"Auditoría: {AUDIT_PATH}")


if __name__ == "__main__":
    main()