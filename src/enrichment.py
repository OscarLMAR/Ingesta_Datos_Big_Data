from __future__ import annotations

import json
from datetime import datetime
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


def normalizar_clave(series: pd.Series) -> pd.Series:
    return series.astype("string").str.strip().str.upper()


def preparar_fuente(
    frame: pd.DataFrame,
    key: str,
    source_name: str,
    audit: list[dict[str, object]],
) -> pd.DataFrame:
    """Normaliza una fuente y registra su cobertura antes del cruce."""
    if key not in frame.columns:
        raise ValueError(f"La fuente {source_name} no contiene la clave {key}")

    frame = frame.copy()
    frame[key] = normalizar_clave(frame[key])
    duplicate_keys = int(frame[key].duplicated().sum())
    frame = frame.drop_duplicates(subset=[key], keep="first")
    audit.append(
        {
            "source": source_name,
            "rows": len(frame),
            "duplicate_keys": duplicate_keys,
            "key": key,
        }
    )
    return frame


def cargar_fuentes(audit: list[dict[str, object]]) -> list[tuple[pd.DataFrame, str, str]]:
    """Lee JSON, XLSX, CSV, XML, HTML y TXT como fuentes independientes."""
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
        [
            {field.tag: field.text for field in country}
            for country in xml_root.findall("country")
        ]
    )

    customer_tables = pd.read_html(
        (SOURCES_DIR / "customer_segments.html").as_uri()
    )
    customer_segments = customer_tables[0]

    promotions = pd.read_csv(
        SOURCES_DIR / "promotions.txt",
        sep="|",
    )

    return [
        (
            preparar_fuente(product_catalog, "StockCode", "product_catalog.json", audit),
            "StockCode",
            "product_catalog.json",
        ),
        (
            preparar_fuente(inventory, "StockCode", "inventory_source.xlsx", audit),
            "StockCode",
            "inventory_source.xlsx",
        ),
        (
            preparar_fuente(country_info, "Country", "country_info.csv", audit),
            "Country",
            "country_info.csv",
        ),
        (
            preparar_fuente(shipping, "Country", "shipping.xml", audit),
            "Country",
            "shipping.xml",
        ),
        (
            preparar_fuente(customer_segments, "CustomerID", "customer_segments.html", audit),
            "CustomerID",
            "customer_segments.html",
        ),
        (
            preparar_fuente(promotions, "StockCode", "promotions.txt", audit),
            "StockCode",
            "promotions.txt",
        ),
    ]


def cruzar_por_clave(
    base: pd.DataFrame,
    source: pd.DataFrame,
    key: str,
    source_name: str,
) -> tuple[pd.DataFrame, dict[str, object]]:
    base_key = f"__key_{key}"
    source_key = f"__key_{key}"
    base = base.copy()
    source = source.copy()
    base[base_key] = normalizar_clave(base[key])
    source[source_key] = normalizar_clave(source[key])
    source = source.drop(columns=[key])
    source_columns = [column for column in source.columns if column != source_key]
    source = source.rename(
        columns={column: f"{column}_{source_name.rsplit('.', 1)[0]}" for column in source_columns}
    )
    matched = int(base[base_key].isin(set(source[source_key].dropna())).sum())
    result = base.merge(source, left_on=base_key, right_on=source_key, how="left")
    result = result.drop(columns=[base_key, source_key])
    return result, {
        "source": source_name,
        "key": key,
        "matched": matched,
        "unmatched": len(base) - matched,
        "columns_added": len(source_columns),
    }


def escribir_auditoria(
    base_rows: int,
    enriched: pd.DataFrame,
    source_audit: list[dict[str, object]],
    join_audit: list[dict[str, object]],
) -> None:
    with AUDIT_PATH.open("w", encoding="utf-8") as report:
        report.write("=" * 68 + "\n")
        report.write("EA3 - AUDITORIA DE ENRIQUECIMIENTO DE DATOS\n")
        report.write("=" * 68 + "\n\n")
        report.write(f"Fecha de ejecución: {datetime.now():%Y-%m-%d %H:%M:%S}\n")
        report.write(f"Dataset base: {BASE_DATA_PATH.relative_to(BASE_DIR)}\n")
        report.write(f"Registros base: {base_rows}\n")
        report.write(f"Registros enriquecidos: {len(enriched)}\n")
        report.write(f"Columnas base: {len(enriched.columns) - sum(item['columns_added'] for item in join_audit)}\n")
        report.write(f"Columnas enriquecidas: {len(enriched.columns)}\n\n")

        report.write("FUENTES LEIDAS\n")
        for item in source_audit:
            report.write(
                f"- {item['source']}: {item['rows']} registros, "
                f"{item['duplicate_keys']} claves duplicadas, clave {item['key']}.\n"
            )

        report.write("\nOPERACIONES DE CRUCE\n")
        for item in join_audit:
            report.write(
                f"- {item['source']} por {item['key']}: "
                f"{item['matched']} coincidencias, {item['unmatched']} sin coincidencia, "
                f"{item['columns_added']} columnas agregadas.\n"
            )

        report.write("\nTRANSFORMACIONES Y OBSERVACIONES\n")
        report.write("- Se normalizaron las claves eliminando espacios y aplicando mayúsculas.\n")
        report.write("- Se conservaron todos los registros base mediante cruces left join.\n")
        report.write("- Las claves duplicadas de cada fuente conservaron la primera ocurrencia.\n")
        report.write("- Las columnas de fuentes se renombran con el origen para evitar colisiones.\n")
        report.write("- El resultado es una muestra representativa de la salida limpia de la Actividad 2.\n")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    base = pd.read_csv(BASE_DATA_PATH)
    base_rows = len(base)
    source_audit: list[dict[str, object]] = []
    join_audit: list[dict[str, object]] = []

    enriched = base.copy()
    for source, key, source_name in cargar_fuentes(source_audit):
        enriched, join_details = cruzar_por_clave(enriched, source, key, source_name)
        join_audit.append(join_details)

    enriched.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")
    escribir_auditoria(base_rows, enriched, source_audit, join_audit)
    print(f"Enriquecimiento completado: {len(enriched)} registros, {len(enriched.columns)} columnas")
    print(f"Salida: {OUTPUT_PATH}")
    print(f"Auditoría: {AUDIT_PATH}")


if __name__ == "__main__":
    main()