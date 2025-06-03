import streamlit as st
import pandas as pd
import pdfplumber
import re
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine


st.title("Análisis y Consolidación de Gastos")

def limpiar_monto(monto):
    if pd.isna(monto):
        return None
    monto = str(monto).replace("$", "").replace(".", "").replace(",", ".").replace(" ", "")
    try:
        return float(monto)
    except:
        return None

def leer_excel(file):
    df = pd.read_excel(file)
    # Renombra columnas para unificación
    df.columns = [c.strip().lower() for c in df.columns]
    df = df.rename(columns={
        "fecha": "vencimiento",
        "categorias": "categoria",
        "provedor": "proveedor",
        "monto": "total"
    })
    # Limpia montos

    # Limpia proveedor y categoría
    df["proveedor"] = df["proveedor"].astype(str).str.strip().str.replace('"', '')
    df["categoria"] = df["categoria"].astype(str).str.strip().str.replace('"', '')
    # Elimina cliente y nro_factura
    return df[["vencimiento", "total", "proveedor", "categoria"]]

def extraer_datos_factura(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        texto = "\n".join([pagina.extract_text() for pagina in pdf.pages])
    datos = {
        "vencimiento": re.search(r"Vencimiento\s+(\d{2}/\d{2}/\d{4})", texto),
        "total": re.search(r"TOTAL UNIFICADO \$ ?([\d\.,]+)", texto),
        "proveedor": "C.E.S.P. Necochea"
    }
    return {
        "vencimiento": datos["vencimiento"].group(1) if datos["vencimiento"] else None,
        "total": float(datos["total"].group(1).replace('.', '').replace(',', '.')) if datos["total"] else None,
        "proveedor": datos["proveedor"],
        "categoria": "Energía Eléctrica"
    }

st.header("Carga de archivos")
excel_file = st.file_uploader("Sube planilla Excel de gastos", type=["xlsx", "xls"])
pdf_files = st.file_uploader("Sube facturas PDF", type="pdf", accept_multiple_files=True)

df_excel = pd.DataFrame()
df_pdfs = pd.DataFrame()

if excel_file:
    df_excel = leer_excel(excel_file)
    st.success("Planilla Excel cargada.")

if pdf_files:
    datos_pdfs = [extraer_datos_factura(pdf) for pdf in pdf_files]
    df_pdfs = pd.DataFrame(datos_pdfs)
    st.success(f"{len(pdf_files)} factura(s) PDF procesadas.")

if not df_excel.empty or not df_pdfs.empty:
    columnas = ["vencimiento", "total", "proveedor", "categoria"]
    for col in columnas:
        if col not in df_excel.columns:
            df_excel[col] = None
        if col not in df_pdfs.columns:
            df_pdfs[col] = None
    df_unificado = pd.concat([df_excel[columnas], df_pdfs[columnas]], ignore_index=True)
    st.write("### Datos Unificados", df_unificado)

    # Guardar en SQLite
    if st.button("Guardar en base de datos SQLite"):
        engine = create_engine("sqlite:///gastos_empresa.db")
        df_unificado.to_sql("gastos", con=engine, if_exists="replace", index=False)
        st.success("Datos guardados en la base de datos SQLite (gastos_empresa.db)")

    # Procesamiento de fechas
    df_unificado["vencimiento"] = pd.to_datetime(df_unificado["vencimiento"], dayfirst=True, errors="coerce")
    df_unificado["mes"] = df_unificado["vencimiento"].dt.to_period("M").astype(str)

    st.subheader("Visualizaciones")

    # Gasto total por mes
    total_mes = df_unificado.groupby("mes")["total"].sum().reset_index()
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    sns.barplot(data=total_mes, x="mes", y="total", palette="viridis", ax=ax1)
    ax1.set_title("Gasto Total por Mes")
    ax1.set_ylabel("Total ($)")
    ax1.set_xlabel("Mes")
    plt.xticks(rotation=45)
    st.pyplot(fig1)

    # Gasto por categoría
    fig2, ax2 = plt.subplots(figsize=(5, 3))
    df_unificado.groupby("categoria")["total"].sum().sort_values().plot(kind="barh", color="skyblue", ax=ax2)
    ax2.set_title("Gasto por Categoría")
    st.pyplot(fig2)

    # Gasto por proveedor
    fig3, ax3 = plt.subplots(figsize=(5, 3))
    df_unificado.groupby("proveedor")["total"].sum().sort_values().plot(kind="barh", color="orange", ax=ax3)
    ax3.set_title("Gasto por Proveedor")
    st.pyplot(fig3)
else:
    st.info("Sube al menos un archivo Excel o PDF para comenzar.")