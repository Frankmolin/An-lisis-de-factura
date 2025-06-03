# Trabajo Práctico: Análisis y Consolidación de Gastos Anuales

## Descripción

Esta aplicación permite analizar y consolidar los gastos anuales de una empresa a partir de dos fuentes principales:  
1. **Planillas de cálculo (Excel)** con datos estructurados sobre gastos mensuales.  
2. **Facturas en formato PDF** que contienen información adicional no consolidada.

El objetivo es construir una solución que permita:
- Leer, limpiar y unificar los datos de gastos desde Excel y PDFs.
- Almacenar toda la información consolidada en una base de datos relacional (SQLite).
- Realizar un análisis exploratorio para obtener métricas útiles (gasto total por mes, categoría, proveedor, etc.).
- Visualizar los resultados de manera clara (gráficos con matplotlib o seaborn).

---

## Tecnologías utilizadas

- **pandas**: Manipulación y limpieza de datos.  
- **openpyxl**: Lectura de archivos Excel.  
- **pdfplumber**: Extracción de texto de facturas PDF.  
- **re**: Extracción de información usando expresiones regulares.  
- **sqlalchemy**: Carga de datos en una base de datos SQLite.  
- **matplotlib** y **seaborn**: Visualización de resultados.  
- **streamlit**: Interfaz web interactiva.

---

## Instalación

1. Clona este repositorio:

```
git clone https://github.com/Frankmolin/An-lisis-de-factura.git
cd An-lisis-de-factura
```
## Instalación de dependencias
```
pip install pandas openpyxl pdfplumber sqlalchemy matplotlib seaborn streamlit
```
## Para ejecutar la aplicación en Streamlit:
```
streamlit run app.py
```
