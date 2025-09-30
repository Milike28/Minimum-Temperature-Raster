"""
Streamlit App - Version sin geopandas
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

st.set_page_config(page_title="Analisis de Heladas Peru", page_icon="❄️", layout="wide")

BASE_DIR = Path("C:/Users/ASUS/OneDrive - Universidad del Pacífico/Tareas Data Science/Minimum-Temperature-Raster")
TABLES_DIR = BASE_DIR / 'data' / 'outputs' / 'tables'
PLOTS_DIR = BASE_DIR / 'data' / 'outputs' / 'plots'

@st.cache_data
def load_data():
    stats = pd.read_csv(TABLES_DIR / 'zonal_statistics.csv')
    policies = pd.read_csv(TABLES_DIR / 'policy_proposals.csv')
    return stats, policies

stats_df, policies_df = load_data()

st.title("❄️ Analisis de Riesgo de Heladas en Peru")
st.markdown("**Analisis de Temperatura Minima (Tmin) por Distrito**")
st.divider()

### SIDEBAR
st.sidebar.header("Filtros")
regions = ['Todos'] + sorted(stats_df['REGION'].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

filtered_df = stats_df.copy() if selected_region == 'Todos' else stats_df[stats_df['REGION'] == selected_region].copy()

### METRICAS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Distritos", f"{len(filtered_df):,}")
col2.metric("Temp Media", f"{filtered_df['mean'].mean():.2f}°C")
col3.metric("Alto Riesgo", f"{len(filtered_df[filtered_df['risk_category'].isin(['High', 'Very High'])]):,}")
col4.metric("Temp Min", f"{filtered_df['min'].min():.2f}°C")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📈 Visualizaciones", "📋 Datos", "🗺️ Mapas", "📜 Politicas"])

with tab1:
    st.header("Visualizaciones")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(filtered_df['mean'], bins=30, color='steelblue', edgecolor='black')
    ax.set_xlabel('Temperatura Media (°C)')
    ax.set_ylabel('Frecuencia')
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

with tab2:
    st.header("Datos")
    st.dataframe(filtered_df[['NAME', 'REGION', 'mean', 'min', 'max', 'risk_category']])
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("Descargar CSV", csv, "datos.csv", "text/csv")

with tab3:
    st.header("Mapas")
    map_img = PLOTS_DIR / '03_choropleth_maps.png'
    if map_img.exists():
        st.image(str(map_img))
    else:
        st.warning("Mapas no disponibles")

with tab4:
    st.header("Politicas Publicas")
    total_budget = policies_df['costo_total_s'].sum()
    st.metric("Presupuesto Total", f"S/ {total_budget:,.0f}")
    for _, row in policies_df.iterrows():
        with st.expander(row['propuesta']):
            st.write(f"**Objetivo:** {row['objetivo']}")
            st.write(f"**Presupuesto:** S/ {row['costo_total_s']:,.0f}")