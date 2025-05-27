import pandas as pd
import pdfplumber
import re
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import seaborn as sns




# === 2. Extraer datos desde una factura PDF ===
def extraer_datos_factura(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        texto = "\n".join([pagina.extract_text() for pagina in pdf.pages])
    
    datos = {
        "cliente": "LOPEZ MARIO GERVASIO",
        "nro_factura": re.search(r"B-\d{4}-\d+", texto),
        "vencimiento": re.search(r"Vencimiento\s+(\d{2}/\d{2}/\d{4})", texto),
        "total": re.search(r"TOTAL UNIFICADO \$ ?([\d\.,]+)", texto),
        "proveedor": "C.E.S.P. Necochea"
    }

    return {
        "cliente": datos["cliente"],
        "nro_factura": datos["nro_factura"].group(0) if datos["nro_factura"] else None,
        "vencimiento": datos["vencimiento"].group(1) if datos["vencimiento"] else None,
        "total": float(datos["total"].group(1).replace('.', '').replace(',', '.')) if datos["total"] else None,
        "proveedor": datos["proveedor"],
        "categoria": "Energía Eléctrica"
    }

# === 3. Unificación de datos ===
def unificar_datos(datos_pdf):
    df_pdf = pd.DataFrame([datos_pdf])

    return df_pdf

# === 4. Guardar en SQLite ===
def guardar_en_sqlite(df, ruta_db="gastos_empresa.db"):
    engine = create_engine(f"sqlite:///{ruta_db}")
    df.to_sql("gastos", con=engine, if_exists="replace", index=False)
    print(f"✅ Datos guardados en {ruta_db}")
    return engine

# === 5. Visualización de resultados ===
def analizar_y_visualizar(df):
    # Asegura que 'vencimiento' sea datetime
    df["vencimiento"] = pd.to_datetime(df["vencimiento"], dayfirst=True, errors="coerce")
    df["mes"] = df["vencimiento"].dt.to_period("M").astype(str)

    # Total por mes
    total_mes = df.groupby("mes")["total"].sum().reset_index()
    plt.figure(figsize=(10, 6))
    sns.barplot(data=total_mes, x="mes", y="total", palette="viridis")
    plt.title("Gasto Total por Mes")
    plt.ylabel("Total ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Gasto por categoría
    plt.figure(figsize=(8, 5))
    df.groupby("categoria")["total"].sum().sort_values().plot(kind="barh", color="skyblue")
    plt.title("Gasto por Categoría")
    plt.tight_layout()
    plt.show()

    # Gasto por proveedor
    plt.figure(figsize=(8, 5))
    df.groupby("proveedor")["total"].sum().sort_values().plot(kind="barh", color="orange")
    plt.title("Gasto por Proveedor")
    plt.tight_layout()
    plt.show()

# === 6. Main ===
def main():

    pdf_path = "factura2 (1).pdf"       # Factura ya subida


    print("📄 Extrayendo datos de factura PDF...")
    datos_pdf = extraer_datos_factura(pdf_path)

    print("📊 Unificando datos...")
    df_unificado = unificar_datos(datos_pdf)

    print("💾 Guardando en SQLite...")
    guardar_en_sqlite(df_unificado)

    print("📈 Mostrando visualizaciones...")
    analizar_y_visualizar(df_unificado)

if __name__ == "__main__":
    main()
