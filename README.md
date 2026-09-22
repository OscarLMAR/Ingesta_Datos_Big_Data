# Ingesta de Datos Big Data

## Descripción

Este proyecto implementa un proceso compuesto por dos etapas:

- EA1 - Ingestión y construcción de una base de datos analítica.
- EA2 - Preprocesamiento y limpieza de datos.

En el proyecto se usan herramientas como:
- Python
- Pandas
- SQLite
- Una fuente de datos accesible mediante API
- GitHub Actions para automatizar la ejecución y generación de evidencias.

La fuente utilizada corresponde al conjunto de datos **Online Retail**, obtenido mediante la API pública de Kaggle.

El flujo completo permite:

1. Obtener los datos desde la API.
2. Almacenar el archivo fuente en formato CSV.
3. Cargar los datos en una base de datos SQLite.
4. Realizar controles de calidad.
5. Aplicar reglas de validación.
6. Transformar los datos para su utilización analítica.
7. Construir un modelo dimensional tipo estrella.
8. Generar evidencias de auditoría.
9. Generar muestras de los datos mediante Pandas.
10. Realizar el preprocesamiento y limpieza correspondiente a la EA2.
11. Generar una muestra de los datos procesados.
12. Generar un informe TXT de las operaciones de limpieza.
13. Automatizar el proceso completo mediante GitHub Actions.

---------------

# Fuente de datos

**Conjunto de datos:** Online Retail

**Fuente:** Kaggle

**API utilizada:**

https://www.kaggle.com/api/v1/datasets/download/vijayuv/onlineretail

La descarga se realiza mediante una solicitud HTTP utilizando la biblioteca requests.

El conjunto de datos original contiene:

541.909 registros
8 columnas

Las columnas originales son:

InvoiceNo
StockCode
Description
Quantity
InvoiceDate
UnitPrice
CustomerID
Country

La regla principal utilizada para identificar facturas canceladas son que el campo InvoiceNo comienza con la letra C.

Tecnologías utilizadas
Python 3.12
Pandas
Requests
SQLite
Git
GitHub
GitHub Actions

SQLite no requiere una dependencia externa porque forma parte de la biblioteca estándar de Python.

EA1 - Ingestión y construcción de la base analítica
Objetivo

La primera etapa tiene como finalidad obtener los datos desde una fuente accesible mediante API, almacenarlos localmente, realizar controles de calidad, aplicar reglas de validación y construir una base de datos analítica utilizando SQLite.

Arquitectura del proceso
## Arquitectura del proceso

```text
API de Kaggle
     │
     ▼
OnlineRetail.csv
     │
     ▼
SQLite
     │
     ▼
stg_online_retail
     │
     ▼
Control de calidad
     │
     ▼
Validación de reglas
     │
     ▼
Transformación
     │
     ├──────────────┐
     ▼              ▼
Dimensiones     FactVentas
     │              │
     └───────┬──────┘
             ▼
     Validación final
             │
             ▼
         Evidencias
             │
             ▼
       GitHub Actions
             │
             ▼
     Base de datos SQLite
```

La base de datos analítica se genera en:

data/retail.db

La tabla de staging utilizada para conservar los registros originales es:

stg_online_retail

Esta tabla contiene:

541.909 registros
Modelo dimensional

El proyecto utiliza un modelo dimensional tipo estrella.

DimFecha

Contiene la información correspondiente a las fechas de las ventas.

Registros generados:

305

Rango de fechas:

2010-12-01 a 2011-12-09
DimCliente

Contiene los clientes identificados mediante CustomerID.

Registros:

4.338
DimProducto

Contiene los productos identificados mediante StockCode.

Registros:

3.922
FactVentas

Contiene el detalle de las ventas válidas.

Registros:

530.104

La granularidad de la tabla corresponde a una línea de producto dentro de una transacción.

El campo TotalVenta se calcula mediante:

TotalVenta = Quantity × UnitPrice
Reglas de limpieza de la EA1

Antes de construir FactVentas se aplican las siguientes reglas:

La factura no debe estar cancelada.
Quantity debe ser mayor que cero.
UnitPrice debe ser mayor que cero.

Los registros que no cumplen estas reglas son excluidos de las ventas válidas.

Resultados:

Registros originales:          541.909
Registros válidos:             530.104
Registros excluidos:            11.805

Los registros sin CustomerID no son descartados, ya que la ausencia de cliente no impide considerar válida una venta.

Resultados de calidad de la EA1

La auditoría inicial identificó:

Registros totales:              541.909
CustomerID nulos:               135.080
Description nulas:                1.454
Cantidad no positiva:            10.624
Precio no positivo:               2.517
Facturas canceladas:              9.288
Grupos duplicados:                4.879

Estas categorías pueden presentar intersecciones; por lo tanto, sus valores no deben sumarse para calcular el total de registros inválidos.

Validación de la carga

La comparación entre la fuente y SQLite produjo:

Registros API:                  541.909
Registros SQLite:               541.909
Diferencia:                           0

Resultado:

APROBADO

La tabla de hechos también fue comparada con los registros válidos:

Registros válidos:              530.104
Registros FactVentas:           530.104
Diferencia:                           0

Resultado:

APROBADO
Validación final del modelo

La validación final produjo:

stg_online_retail:               541.909
ventas_limpias:                  530.104
DimFecha:                            305
DimCliente:                       4.338
DimProducto:                      3.922
FactVentas:                      530.104
Integridad referencial
DateID inválido:                     0
ProductoID inválido:                 0
ClienteID inválido:                  0
Reglas de calidad después de la transformación
Cantidades <= 0:                    0
Precios <= 0:                        0
Facturas canceladas:                0
TotalVenta incorrecto:              0

Valor total de ventas:

10.666.684,54
EA2 - Preprocesamiento y limpieza de datos
Objetivo

La segunda etapa del proyecto utiliza como fuente la tabla stg_online_retail de la base de datos SQLite generada durante la EA1.

El objetivo es realizar:

análisis exploratorio de calidad;
identificación de duplicados;
identificación de valores nulos;
revisión de tipos de datos;
validación de fechas;
detección de valores no positivos;
detección de valores atípicos;
corrección de tipos;
tratamiento de valores nulos;
eliminación de duplicados;
aplicación de reglas de limpieza;
generación de nuevas variables;
generación de evidencias.

El procesamiento se implementa mediante Python y Pandas en:

src/cleaning.py
Fuente utilizada en la EA2

La EA2 utiliza la tabla:

stg_online_retail

Esta tabla contiene los registros originales cargados durante la EA1.

Registros procesados:

541.909

La utilización de stg_online_retail permite realizar el preprocesamiento sobre los datos antes de las transformaciones específicas utilizadas para construir el modelo dimensional.

Análisis inicial de calidad de la EA2

El análisis exploratorio inicial produjo los siguientes resultados:

Registros iniciales:          541.909
Duplicados exactos:              5.268
CustomerID nulos:              135.080
Description nulas:               1.454
Quantity <= 0:                  10.624
UnitPrice <= 0:                  2.517
Fechas inválidas:                    0
Tipos iniciales

Los tipos identificados inicialmente fueron:

InvoiceNo        str
StockCode        str
Description      str
Quantity         int64
InvoiceDate      str
UnitPrice        float64
CustomerID       float64
Country          str
Detección de valores atípicos

Se utilizó el método del rango intercuartílico (IQR) para identificar posibles valores atípicos.

Quantity
Q1:                  1.0
Q3:                 10.0
IQR:                 9.0
Límite inferior:   -12.5
Límite superior:    23.5
Outliers:           58.619
UnitPrice
Q1:                  1.25
Q3:                  4.13
IQR:                 2.88
Límite inferior:    -3.07
Límite superior:     8.45
Outliers:           39.627

Los valores identificados mediante IQR no fueron eliminados automáticamente.

La detección de un valor atípico no implica necesariamente que el registro sea inválido desde el punto de vista del negocio. Por esta razón, los outliers fueron documentados y conservados cuando no incumplían las reglas de limpieza definidas.

Reglas de limpieza de la EA2

Se aplicaron las siguientes reglas:

Eliminar registros duplicados exactos.
Corregir los tipos de datos.
Estandarizar campos de texto.
Convertir InvoiceDate a formato de fecha y hora.
Reemplazar valores nulos de Description por SIN DESCRIPCION.
Mantener CustomerID como campo nullable cuando no existe información del cliente.
Eliminar registros con Quantity <= 0.
Eliminar registros con UnitPrice <= 0.
Eliminar registros con fechas inválidas.
Estandarizar el campo Country.
Crear el campo calculado TotalVenta.
Ordenar los registros por fecha, factura y producto.
Tratamiento de valores nulos
Description

Los valores nulos de Description se reemplazan por:

SIN DESCRIPCION

De esta forma se conserva el registro sin eliminar la transacción debido únicamente a la ausencia de una descripción.

CustomerID

Los registros sin CustomerID se mantienen.

El identificador del cliente se convierte a un tipo entero nullable para conservar correctamente los registros que no contienen información de cliente.

Esto permite diferenciar entre:

Cliente identificado

y:

Cliente no informado

sin eliminar la transacción.

Corrección de tipos

Durante el proceso se realizan las siguientes conversiones:

InvoiceDate → datetime
CustomerID  → Int64 nullable
Quantity    → Int64
UnitPrice   → float

Los campos de texto también son estandarizados mediante eliminación de espacios innecesarios.

Intersección de reglas

El análisis de intersecciones permitió identificar:

Duplicados:                         5.268
Duplicados + cantidad <= 0:            37
Duplicados + precio <= 0:               5
Cantidad <= 0 + precio <= 0:        1.336
Cantidad <= 0 + canceladas:          9.288
Precio <= 0 + canceladas:                 0
Canceladas:                         9.288

Los registros que incumplen al menos una regla de limpieza fueron:

17.031

Los registros que cumplen todas las reglas fueron:

524.878

Las categorías presentan intersecciones, por lo que no deben sumarse individualmente.

Transformación adicional

Se creó el campo:

TotalVenta

mediante la operación:

TotalVenta = Quantity × UnitPrice

Este campo permite representar el valor monetario correspondiente a cada línea de venta.

Resultado final de la limpieza

Después de aplicar las reglas de preprocesamiento:

Registros iniciales:          541.909
Registros finales:             524.878
Registros eliminados:           17.031
Reducción:                         3,14 %

La reducción corresponde a los registros que incumplieron al menos una de las reglas de limpieza definidas.

Evidencia de datos procesados

La EA2 genera una muestra de 100 registros:

src/xlsx/cleaned_data.csv

El archivo contiene 9 columnas:

InvoiceNo
StockCode
Description
Quantity
InvoiceDate
UnitPrice
CustomerID
Country
TotalVenta

La muestra generada fue validada verificando:

Registros:                    100
Duplicados:                     0
Quantity <= 0:                  0
UnitPrice <= 0:                 0
TotalVenta nulos:               0
Auditoría de limpieza

La auditoría de la EA2 se genera en:

src/static/auditoria/cleaning_report.txt

El informe documenta:

cantidad de registros iniciales;
duplicados identificados;
valores nulos;
tipos de datos;
fechas inválidas;
cantidades no positivas;
precios no positivos;
facturas canceladas;
valores atípicos;
reglas de limpieza;
registros eliminados;
registros finales;
transformaciones realizadas;
validaciones posteriores.
Trazabilidad entre EA1 y EA2

Las dos actividades permanecen integradas dentro del mismo proyecto.

El flujo completo es:

                         EA1
                          │
                          ▼
                   API de Kaggle
                          │
                          ▼
                  OnlineRetail.csv
                          │
                          ▼
                       SQLite
                          │
                          ▼
                  stg_online_retail
                          │
                          ▼
                 Modelo analítico
                          │
                          ▼
                    FactVentas
                          │
                          │
                          ▼
                         EA2
                          │
                          ▼
                Análisis de calidad
                          │
                          ▼
                Corrección de tipos
                          │
                          ▼
                 Tratamiento nulos
                          │
                          ▼
               Eliminación duplicados
                          │
                          ▼
              Reglas de limpieza
                          │
                          ▼
                  Transformaciones
                          │
                          ▼
                cleaned_data.csv
                          │
                          ▼
             cleaning_report.txt

La EA2 complementa la EA1 y no reemplaza la implementación anterior.

Evidencias generadas

El proyecto genera archivos de evidencia correspondientes a las dos actividades.

Evidencias EA1
Base de datos
data/retail.db

Contiene las tablas de puesta en escena, transformación, dimensiones y hechos.

Muestra de ingestión
data/muestra_ingestion.csv

Contiene una muestra de 100 registros generada mediante Pandas.

Auditoría de extracción
data/auditoria_extraccion.json

Registra información sobre la fuente y los registros obtenidos.

Auditoría de carga
data/auditoria_carga.json

Compara los registros del CSV con los registros almacenados en SQLite.

Auditoría de calidad
data/auditoria_calidad.json

Registra los resultados de los controles de calidad iniciales.

Auditoría final
data/auditoria_final.json

Contiene la validación final del modelo analítico.

Auditoría TXT
src/static/auditoria/ingestion.txt

Contiene la comparación entre los registros extraídos y almacenados.

Resultado:

API:        541.909
SQLite:     541.909
Diferencia:      0

Válidos:    530.104
FactVentas: 530.104
Diferencia:      0

Estado: APROBADO
Evidencias EA2
Muestra limpia
src/xlsx/cleaned_data.csv

Contiene una muestra de los datos después del proceso de limpieza y transformación.

Auditoría de limpieza
src/static/auditoria/cleaning_report.txt

Documenta el análisis de calidad, las reglas de limpieza aplicadas, las transformaciones y los resultados antes y después del procesamiento.

Estructura del proyecto

```text
Ingesta_Datos_Big_Data/
│
├── .github/
│   └── workflows/
│       └── bigdata.yml
│
├── data/
│   ├── OnlineRetail.csv
│   ├── retail.db
│   ├── muestra_ingestion.csv
│   ├── auditoria_extraccion.json
│   ├── auditoria_carga.json
│   ├── auditoria_calidad.json
│   └── auditoria_final.json
│
├── src/
│   ├── ingestion.py
│   ├── cleaning.py
│   │
│   ├── static/
│   │   └── auditoria/
│   │       ├── ingestion.txt
│   │       └── cleaning_report.txt
│   │
│   ├── xlsx/
│   │   └── cleaned_data.csv
│   │
│   └── db/
│       ├── database.py
│       ├── quality.py
│       ├── validation.py
│       ├── transform.py
│       ├── dimensions.py
│       ├── fact.py
│       ├── validation_final.py
│       ├── indexes.py
│       ├── muestra.py
│       └── auditoria_txt.py
│
├── .gitignore
├── README.md
├── requirements.txt
└── setup.py
```

Nota: Los archivos OnlineRetail.csv y retail.db son archivos generados durante la ejecución y se encuentran excluidos del control de versiones mediante .gitignore. En GitHub Actions son reconstruidos durante el proceso automatizado.

Instalación
1. Clonar el repositorio
git clone https://github.com/Natalia890c/Ingesta_Datos_Big_Data.git

Ingresar al proyecto:

cd Ingesta_Datos_Big_Data
2. Crear entorno virtual

En Windows:

python -m venv .venv

Activar el entorno:

.venv\Scripts\activate
3. Instalar dependencias
pip install -r requirements.txt

Las dependencias principales son:

pandas
requests
Ejecución local
EA1

El proceso de ingestión y construcción de la base analítica puede ejecutarse mediante:

python src/ingestion.py
python src/db/database.py
python src/db/quality.py
python src/db/validation.py
python src/db/transform.py
python src/db/dimensions.py
python src/db/fact.py
python src/db/validation_final.py
python src/db/indexes.py
python src/db/muestra.py
python src/db/auditoria_txt.py
EA2

Después de disponer de la base de datos SQLite generada en la EA1, ejecutar:

python src/cleaning.py

El script:

Extrae los datos desde stg_online_retail.
Analiza la calidad inicial.
Corrige los tipos de datos.
Aplica las reglas de limpieza.
Realiza las transformaciones adicionales.
Genera las evidencias de la EA2.

Los archivos generados son:

src/xlsx/cleaned_data.csv
src/static/auditoria/cleaning_report.txt

EA3 - Enriquecimiento

Con la muestra limpia de la Actividad 2 disponible, ejecutar:

python src/enrichment.py

El script lee seis fuentes complementarias en formatos JSON, XLSX, CSV, XML, HTML y TXT desde `data/fuentes_enriquecimiento`. La fuente XLSX se construye desde su semilla CSV si aún no existe, lo que permite reproducirla en un entorno limpio. Las claves de integración son:

- `StockCode`: catálogo de productos, inventario y promociones.
- `Country`: región, tasa de impuesto y condiciones de envío.
- `CustomerID`: segmento y nivel de fidelidad.

Las claves se normalizan con eliminación de espacios y mayúsculas. Se aplican cruces `left join` para conservar todos los registros de la base, se eliminan claves duplicadas de cada fuente conservando la primera ocurrencia y se renombran las columnas con el origen.

Las evidencias de EA3 son:

src/xlsx/enriched_data.csv
src/static/auditoria/enrichment_report.txt

El reporte contiene el número de registros base y enriquecidos, las fuentes leídas, claves utilizadas, coincidencias, diferencias, columnas agregadas y transformaciones aplicadas.

Automatización con GitHub Actions

El proyecto utiliza GitHub Actions para automatizar el proceso completo de las tres etapas del proyecto.

El workflow se encuentra en:

.github/workflows/bigdata.yml

El nombre actual del workflow es:

Big Data - Ingesta, Preprocesamiento y Evidencias

El flujo se ejecuta automáticamente cuando se realiza un push a la rama main.

También puede ejecutarse manualmente mediante workflow_dispatch.

Flujo automatizado

El workflow realiza las siguientes etapas:

Instalación de dependencias
        ↓
Extracción desde API
        ↓
Carga en SQLite
        ↓
Control de calidad EA1
        ↓
Validación EA1
        ↓
Transformación
        ↓
Creación de dimensiones
        ↓
Creación de FactVentas
        ↓
Validación final
        ↓
Creación de índices
        ↓
Generación de muestra EA1
        ↓
Generación de auditoría EA1
        ↓
Preprocesamiento y limpieza EA2
        ↓
Generación de cleaned_data.csv
        ↓
Generación de cleaning_report.txt
        ↓
Enriquecimiento con seis fuentes EA3
        ↓
Generación de enriched_data.csv
        ↓
Generación de enrichment_report.txt
        ↓
Verificación de evidencias
        ↓
Publicación del artifact

Este flujo permite reconstruir la base de datos y ejecutar las EA1, EA2 y EA3 desde un entorno limpio de GitHub Actions.

Artifact generado

El workflow publica las evidencias mediante GitHub Actions.

El artifact generado actualmente es:

evidencias-proyecto-big-data

El artifact contiene evidencias correspondientes a las tres etapas:

retail.db
muestra_ingestion.csv
auditoria_extraccion.json
auditoria_carga.json
auditoria_calidad.json
auditoria_final.json
src/static/auditoria/ingestion.txt
src/xlsx/cleaned_data.csv
src/static/auditoria/cleaning_report.txt
src/xlsx/enriched_data.csv
src/static/auditoria/enrichment_report.txt
Verificación de GitHub Actions

Para comprobar una ejecución:

Ingresar al repositorio en GitHub.
Seleccionar la pestaña Actions.
Seleccionar el workflow Big Data - Ingesta, Preprocesamiento y Evidencias.
Abrir la ejecución correspondiente.
Revisar que todos los pasos finalicen correctamente.
Consultar el artifact generado al finalizar el flujo.

La ejecución automatizada permite comprobar que las etapas de la EA1, EA2 y EA3 pueden ejecutarse de manera reproducible. El artifact `evidencias-proyecto-big-data` conserva la muestra enriquecida y su auditoría para revisión.

Resultados finales
Resultados EA1
Registros extraídos:             541.909
Registros almacenados:            541.909
Diferencia:                            0

Registros válidos:               530.104
Registros en FactVentas:         530.104
Diferencia:                            0

Estado final:                    APROBADO
Resultados EA2
Registros iniciales:             541.909
Registros finales:               524.878
Registros eliminados:             17.031
Reducción:                          3,14 %

Evidencias generadas:

src/xlsx/cleaned_data.csv
src/static/auditoria/cleaning_report.txt
src/xlsx/enriched_data.csv
src/static/auditoria/enrichment_report.txt
Conclusión

El proyecto implementa un flujo reproducible de procesamiento de datos que integra:

ingestión mediante API;
almacenamiento en SQLite;
controles de calidad;
validación de datos;
transformación;
modelado dimensional;
generación de una tabla de hechos;
preprocesamiento;
tratamiento de valores nulos;
eliminación de duplicados;
corrección de tipos;
detección de valores atípicos;
generación de variables derivadas;
generación de muestras;
generación de auditorías;
automatización mediante GitHub Actions.

La arquitectura mantiene la continuidad entre la EA1 y la EA2 dentro del mismo repositorio.

La EA2 utiliza los datos generados durante la EA1 y agrega una etapa específica de preprocesamiento y limpieza, junto con sus respectivas evidencias.

De esta manera, el proyecto conserva la trazabilidad completa desde la fuente de datos hasta los resultados procesados y las evidencias generadas automáticamente.
