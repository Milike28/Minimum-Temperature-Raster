"""
Dashboard Heladas Peru
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(page_title="Heladas Peru", page_icon="❄️", layout="wide")

# RUTA RELATIVA (funciona en Windows Y Linux)
BASE_DIR = Path(__file__).parent.parent
TABLES = BASE_DIR / 'data' / 'outputs' / 'tables'

@st.cache_data
def load_data():
    return (
        pd.read_csv(TABLES / 'zonal_statistics.csv'),
        pd.read_csv(TABLES / 'policy_proposals.csv')
    )

stats, policies = load_data()

st.title("❄️ Análisis de Riesgo de Heladas en Perú")
st.divider()

# FILTROS
st.sidebar.header("Filtros")
regions = ['Todos'] + sorted(stats['REGION'].unique().tolist())
sel = st.sidebar.selectbox("Región", regions)
df = stats if sel == 'Todos' else stats[stats['REGION'] == sel]

# MÉTRICAS
c1, c2, c3, c4 = st.columns(4)
c1.metric("Distritos", f"{len(df):,}")
c2.metric("Temp Media", f"{df['mean'].mean():.2f}°C")
c3.metric("Alto Riesgo", f"{len(df[df['risk_category'].isin(['High','Very High'])]):,}")
c4.metric("Temp Mínima", f"{df['min'].min():.2f}°C")

st.divider()

tab1, tab2, tab3 = st.tabs(["📊 Gráficos", "📋 Datos", "📜 Políticas"])

with tab1:
    fig, ax = plt.subplots(figsize=(10,5))
    ax.hist(df['mean'], bins=30, color='steelblue', edgecolor='black')
    ax.set_xlabel('Temperatura Media (°C)')
    ax.set_ylabel('Frecuencia')
    ax.grid(alpha=0.3)
    st.pyplot(fig)
    
    st.subheader("Top 15 Distritos Más Fríos")
    st.dataframe(df.nsmallest(15, 'mean')[['NAME','REGION','mean','risk_category']])

with tab2:
    st.dataframe(df[['NAME','REGION','mean','min','max','frost_risk_index','risk_category']], 
                 use_container_width=True, height=400)
    st.download_button("📥 CSV", df.to_csv(index=False).encode(), "heladas.csv")

with tab3:
    c1, c2 = st.columns(2)
    c1.metric("Presupuesto", f"S/ {policies['costo_total_s'].sum():,.0f}")
    c2.metric("Beneficiarios", f"{policies['beneficiarios'].sum():,}")
    for _, r in policies.iterrows():
        with st.expander(f"**{r['propuesta']}**"):
            st.write(f"**Costo:** S/ {r['costo_total_s']:,.0f}")