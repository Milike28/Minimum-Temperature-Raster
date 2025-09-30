"""
Streamlit App - Dashboard de Heladas Peru (Sin Geopandas)
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Analisis Heladas Peru", page_icon="❄️", layout="wide")

BASE_DIR = Path(__file__).parent.parent
TABLES_DIR = BASE_DIR / 'data' / 'outputs' / 'tables'
PLOTS_DIR = BASE_DIR / 'data' / 'outputs' / 'plots'

@st.cache_data
def load_data():
    stats = pd.read_csv(TABLES_DIR / 'zonal_statistics.csv')
    policies = pd.read_csv(TABLES_DIR / 'policy_proposals.csv')
    return stats, policies

stats_df, policies_df = load_data()

st.title("❄️ Analisis de Riesgo de Heladas en Peru")
st.divider()

### SIDEBAR
st.sidebar.header("Filtros")
regions = ['Todos'] + sorted(stats_df['REGION'].unique().tolist())
selected_region = st.sidebar.selectbox("Region", regions)

filtered_df = stats_df.copy() if selected_region == 'Todos' else stats_df[stats_df['REGION'] == selected_region]

### METRICAS
col1, col2, col3, col4 = st.columns(4)
col1.metric("Distritos", f"{len(filtered_df):,}")
col2.metric("Temp Media", f"{filtered_df['mean'].mean():.2f}°C")
high_risk_count = len(filtered_df[filtered_df['risk_category'].isin(['High', 'Very High'])])
col3.metric("Alto Riesgo", f"{high_risk_count:,}")
col4.metric("Temp Min", f"{filtered_df['min'].min():.2f}°C")

st.divider()

tab1, tab2, tab3 = st.tabs(["📈 Graficos", "📋 Datos", "📜 Politicas"])

with tab1:
    st.header("Distribucion de Temperatura")
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(filtered_df['mean'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
    ax.axvline(filtered_df['mean'].mean(), color='red', linestyle='--', label=f'Media: {filtered_df["mean"].mean():.2f}°C')
    ax.set_xlabel('Temperatura Media (°C)')
    ax.set_ylabel('Frecuencia')
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    
    st.subheader("Top 15 Distritos Mas Frios")
    top15 = filtered_df.nsmallest(15, 'mean')[['NAME', 'REGION', 'mean', 'risk_category']]
    st.dataframe(top15, use_container_width=True)

with tab2:
    st.header("Estadisticas por Distrito")
    display_cols = ['NAME', 'REGION', 'mean', 'min', 'max', 'std', 'frost_risk_index', 'risk_category']
    st.dataframe(filtered_df[display_cols].sort_values('frost_risk_index', ascending=False), use_container_width=True, height=400)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Descargar CSV", csv, "heladas_peru.csv", "text/csv")

with tab3:
    st.header("Propuestas de Politicas Publicas")
    
    total_budget = policies_df['costo_total_s'].sum()
    total_beneficiaries = policies_df['beneficiarios'].sum()
    
    col1, col2 = st.columns(2)
    col1.metric("Presupuesto Total", f"S/ {total_budget:,.0f}")
    col2.metric("Beneficiarios", f"{total_beneficiaries:,}")
    
    st.divider()
    
    for idx, row in policies_df.iterrows():
        with st.expander(f"**{row['propuesta']}**"):
            st.write(f"**Objetivo:** {row['objetivo']}")
            st.write(f"**Poblacion:** {row['poblacion_objetivo']}")
            st.write(f"**Intervencion:** {row['intervencion']}")
            st.write(f"**Costo Total:** S/ {row['costo_total_s']:,.0f}")
            st.write(f"**Beneficiarios:** {row['beneficiarios']:,}")
            st.write(f"**KPIs:** {row['kpi']}")
            st.write(f"**Plazo:** {row['plazo_años']} años")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(len(policies_df)), policies_df['costo_total_s'] / 1e6, color=['steelblue', 'orange', 'green'], edgecolor='black')
    ax.set_xticks(range(len(policies_df)))
    ax.set_xticklabels(policies_df['propuesta'].str[:30], rotation=15, ha='right')
    ax.set_ylabel('Presupuesto (Millones S/)')
    ax.grid(True, alpha=0.3, axis='y')
    st.pyplot(fig)

st.caption("Analisis de Riesgo de Heladas en Peru - Temperatura Minima (Tmin)")