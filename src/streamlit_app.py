"""
Streamlit App - Dashboard Heladas Peru
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Heladas Peru", page_icon="❄️", layout="wide")

BASE_DIR = Path("C:/Users/ASUS/OneDrive - Universidad del Pacífico/Tareas Data Science/Minimum-Temperature-Raster")
TABLES = BASE_DIR / 'data' / 'outputs' / 'tables'
PLOTS = BASE_DIR / 'data' / 'outputs' / 'plots'

@st.cache_data
def load_data():
    return (
        pd.read_csv(TABLES / 'zonal_statistics.csv'),
        pd.read_csv(TABLES / 'policy_proposals.csv')
    )

stats, policies = load_data()

st.title("❄️ Análisis de Riesgo de Heladas en Perú")
st.divider()

### FILTROS
st.sidebar.header("Filtros")
regions = ['Todos'] + sorted(stats['REGION'].unique().tolist())
sel_region = st.sidebar.selectbox("Región", regions)
df = stats if sel_region == 'Todos' else stats[stats['REGION'] == sel_region]

### MÉTRICAS
c1, c2, c3, c4 = st.columns(4)
c1.metric("Distritos", f"{len(df):,}")
c2.metric("Temp Media", f"{df['mean'].mean():.2f}°C")
c3.metric("Alto Riesgo", f"{len(df[df['risk_category'].isin(['High','Very High'])]):,}")
c4.metric("Temp Mínima", f"{df['min'].min():.2f}°C")

st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "📋 Datos", "📜 Políticas"])

with tab1:
    st.header("Distribución de Temperatura")
    fig, ax = plt.subplots(figsize=(10,5))
    ax.hist(df['mean'], bins=30, color='steelblue', edgecolor='black')
    ax.set_xlabel('Temperatura Media (°C)')
    ax.set_ylabel('Frecuencia')
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    
    st.subheader("Top 15 Distritos Más Fríos")
    top15 = df.nsmallest(15, 'mean')[['NAME','REGION','mean','risk_category']]
    st.dataframe(top15, use_container_width=True)

with tab2:
    st.header("Estadísticas por Distrito")
    cols = ['NAME','REGION','mean','min','max','std','frost_risk_index','risk_category']
    st.dataframe(df[cols].sort_values('frost_risk_index', ascending=False), 
                 use_container_width=True, height=400)
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", csv, "heladas_peru.csv")

with tab3:
    st.header("Propuestas de Políticas Públicas")
    c1, c2 = st.columns(2)
    c1.metric("Presupuesto Total", f"S/ {policies['costo_total_s'].sum():,.0f}")
    c2.metric("Beneficiarios", f"{policies['beneficiarios'].sum():,}")
    st.divider()
    
    for _, row in policies.iterrows():
        with st.expander(f"**{row['propuesta']}**"):
            st.write(f"**Objetivo:** {row['objetivo']}")
            st.write(f"**Intervención:** {row['intervencion']}")
            st.write(f"**Costo:** S/ {row['costo_total_s']:,.0f}")
            st.write(f"**Beneficiarios:** {row['beneficiarios']:,}")