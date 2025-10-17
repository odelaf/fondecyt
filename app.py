import streamlit as st
import pandas as pd

# Configuración de la app
st.set_page_config(page_title="Clasificación de Proyectos FONDECYT", layout="wide")
st.title("📚 Clasificación Jurídica de Proyectos FONDECYT")
st.markdown("Explora los proyectos clasificados por materia legal. Puedes filtrar y leer el texto completo sin perder el contexto.")

# === CARGA DE DATOS ===
@st.cache_data
def load_data():
    return pd.read_csv("classified_proyectos_500w_explained.csv")

df = load_data()

# === FILTROS LATERALES ===
st.sidebar.header("🔍 Filtros de búsqueda")

# Usar predicted_subject en lugar de assigned_subject
materias = sorted(df["predicted_subject"].dropna().unique())
materia_seleccionada = st.sidebar.selectbox("Materia legal:", ["Todas"] + list(materias))

keyword = st.sidebar.text_input("Buscar palabra clave en el texto:")

# Filtro por confianza
confianza_minima = st.sidebar.slider("Confianza mínima (%):", 0, 100, 0)

# === FILTRADO ===
df_filtrado = df.copy()

if materia_seleccionada != "Todas":
    df_filtrado = df_filtrado[df_filtrado["predicted_subject"] == materia_seleccionada]

if keyword:
    df_filtrado = df_filtrado[df_filtrado["relevant_text_segment"].str.contains(keyword, case=False, na=False)]

# Filtrar por confianza
df_filtrado = df_filtrado[df_filtrado["confidence_pct"] >= confianza_minima]

st.markdown(f"**Mostrando {len(df_filtrado)} de {len(df)} proyectos.**")

# === VISUALIZACIÓN ===
st.markdown("### 📄 Lista de proyectos")

# Mostrar cada proyecto en un bloque expandible
for i, row in df_filtrado.iterrows():
    with st.expander(f"**{row['filename']}** — {row['predicted_subject']} (Confianza: {row['confidence_pct']}%)"):
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.write("**Texto relevante:**")
            st.write(row["relevant_text_segment"])
        
        with col2:
            st.write("**Detalles de clasificación:**")
            st.write(f"**Materia:** {row['predicted_subject']}")
            st.write(f"**Puntuación:** {row['top_score']}")
            st.write(f"**Segunda opción:** {row['second_score']}")
            st.write(f"**Confianza:** {row['confidence_pct']}%")
            st.write("**Palabras clave:**")
            st.write(row["matched_keywords_summary"])
            st.write("**Explicación:**")
            st.write(row["explanation"])

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
conteo = df["predicted_subject"].value_counts().reset_index()
conteo.columns = ["Materia legal", "Cantidad de proyectos"]
st.bar_chart(conteo.set_index("Materia legal"))

# === ESTADÍSTICAS ADICIONALES ===
st.markdown("### 📈 Estadísticas de clasificación")

col1, col2, col3 = st.columns(3)

with col1:
    confianza_promedio = df["confidence_pct"].mean()
    st.metric("Confianza promedio", f"{confianza_promedio:.1f}%")

with col2:
    st.metric("Total de proyectos", len(df))

with col3:
    st.metric("Materias distintas", len(materias))

# Distribución de confianza
st.markdown("### 📊 Distribución de niveles de confianza")
hist_values = pd.cut(df["confidence_pct"], bins=[0, 50, 70, 85, 100], 
                    labels=["Baja (0-50%)", "Media (51-70%)", "Alta (71-85%)", "Muy Alta (86-100%)"])
conf_dist = hist_values.value_counts().sort_index()
st.bar_chart(conf_dist)
