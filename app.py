import streamlit as st
import pandas as pd

# Configuración de la app
st.set_page_config(page_title="Clasificación de Proyectos FONDECYT", layout="wide")
st.title("📚 Clasificación Jurídica de Proyectos FONDECYT")
st.markdown("Explora los 240 proyectos clasificados por materia legal. Puedes filtrar y leer el texto completo sin perder el contexto.")

# === CARGA DE DATOS ===
@st.cache_data
def load_data():
    return pd.read_csv("classified_proyectos_500w_explained.csv")

df = load_data()

# === FILTROS LATERALES ===
st.sidebar.header("🔍 Filtros de búsqueda")

materias = sorted(df["assigned_subject"].dropna().unique())
materia_seleccionada = st.sidebar.selectbox("Materia legal:", ["Todas"] + list(materias))

keyword = st.sidebar.text_input("Buscar palabra clave en el texto:")

# === FILTRADO ===
df_filtrado = df.copy()

if materia_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["assigned_subject"] == materia_seleccionada]

if keyword:
    df_filtrado = df_filtrado[df_filtrado["relevant_text_segment"].str.contains(keyword, case=False, na=False)]

st.markdown(f"**Mostrando {len(df_filtrado)} de {len(df)} proyectos.**")

# === VISUALIZACIÓN ===
st.markdown("### 📄 Lista de proyectos")

# Mostrar cada proyecto en un bloque expandible
for i, row in df_filtrado.iterrows():
    with st.expander(f"**{row['filename']}** — {row['assigned_subject']}"):
        st.write(row["relevant_text_segment"])

# === DESCARGA DE RESULTADOS ===
def convertir_csv(df):
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

csv_descarga = convertir_csv(df_filtrado)

st.download_button(
    label="⬇️ Descargar resultados filtrados (CSV)",
    data=csv_descarga,
    file_name="proyectos_filtrados.csv",
    mime="text/csv"
)

# === DISTRIBUCIÓN GENERAL ===
st.markdown("### 📊 Distribución general por materia legal")
conteo = df["assigned_subject"].value_counts().reset_index()
conteo.columns = ["Materia legal", "Cantidad de proyectos"]
st.bar_chart(conteo.set_index("Materia legal"))
