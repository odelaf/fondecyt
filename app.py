import streamlit as st
import pandas as pd

# Título de la aplicación
st.set_page_config(page_title="Clasificación de Proyectos FONDECYT", layout="wide")
st.title("📚 Clasificación Jurídica de Proyectos FONDECYT")
st.markdown("Visualiza, filtra y descarga la clasificación de los 240 proyectos según su materia legal principal.")

# Cargar el archivo CSV
@st.cache_data
def load_data():
    return pd.read_csv("classified_proyectos.csv")

df = load_data()

# Filtros laterales
st.sidebar.header("🔍 Filtros de búsqueda")

# Filtrar por materia legal
materias = sorted(df["assigned_subject"].dropna().unique())
materia_seleccionada = st.sidebar.selectbox("Selecciona una materia legal:", ["Todas"] + list(materias))

# Filtro adicional por palabra clave
keyword = st.sidebar.text_input("Buscar por palabra clave en el texto relevante:")

# Aplicar filtros
df_filtrado = df.copy()

if materia_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["assigned_subject"] == materia_seleccionada]

if keyword:
    df_filtrado = df_filtrado[df_filtrado["relevant_text_segment"].str.contains(keyword, case=False, na=False)]

# Mostrar resumen
st.markdown(f"**Proyectos mostrados:** {len(df_filtrado)} de {len(df)} totales")

# Mostrar tabla
st.dataframe(df_filtrado, use_container_width=True, height=600)

# Botón para descargar CSV filtrado
def convertir_csv(df):
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")

csv_descarga = convertir_csv(df_filtrado)
st.download_button(
    label="⬇️ Descargar resultados filtrados en CSV",
    data=csv_descarga,
    file_name="proyectos_filtrados.csv",
    mime="text/csv"
)

# Gráfico opcional (distribución de materias)
st.markdown("### 📊 Distribución general por materia legal")
conteo = df["assigned_subject"].value_counts().reset_index()
conteo.columns = ["Materia legal", "Cantidad de proyectos"]
st.bar_chart(conteo.set_index("Materia legal"))
