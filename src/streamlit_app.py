"""
Streamlit App - Dashboard Interactivo de Analisis de Heladas en Peru
"""

import streamlit as st
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

### Configuracion de pagina
st.set_page_config(
    page_title="Analisis de Heladas Peru",
    page_icon="❄️",
    layout="wide"
)

### Rutas
BASE_DIR = Path("C:/Users/ASUS/OneDrive - Universidad del Pacífico/Tareas Data Science/Minimum-Temperature-Raster")
DATA_DIR = BASE_DIR / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
TABLES_DIR = DATA_DIR / 'outputs' / 'tables'
PLOTS_DIR = DATA_DIR / 'outputs' / 'plots'

### Cargar datos
@st.cache_data
def load_data():
    stats = pd.read_csv(TABLES_DIR / 'zonal_statistics.csv')
    districts = gpd.read_file(PROCESSED_DIR / 'peru_districts.gpkg')
    policies = pd.read_csv(TABLES_DIR / 'policy_proposals.csv')
    return stats, districts, policies

stats_df, districts_gdf, policies_df = load_data()

### HEADER
st.title("❄️ Analisis de Riesgo de Heladas en Peru")
st.markdown("**Analisis de Temperatura Minima (Tmin) por Distrito**")
st.divider()

### SIDEBAR FILTERS
st.sidebar.header("Filtros")

### Filtro por region
regions = ['Todos'] + sorted(stats_df['REGION'].unique().tolist())
selected_region = st.sidebar.selectbox("Seleccionar Region", regions)

### Filtro por categoria de riesgo
risk_cats = ['Todos'] + sorted(stats_df['risk_category'].unique().tolist())
selected_risk = st.sidebar.selectbox("Categoria de Riesgo", risk_cats)

### Filtro por temperatura
temp_range = st.sidebar.slider(
    "Rango de Temperatura Media (°C)",
    float(stats_df['mean'].min()),
    float(stats_df['mean'].max()),
    (float(stats_df['mean'].min()), float(stats_df['mean'].max()))
)

### Aplicar filtros
filtered_df = stats_df.copy()

if selected_region != 'Todos':
    filtered_df = filtered_df[filtered_df['REGION'] == selected_region]

if selected_risk != 'Todos':
    filtered_df = filtered_df[filtered_df['risk_category'] == selected_risk]

filtered_df = filtered_df[
    (filtered_df['mean'] >= temp_range[0]) & 
    (filtered_df['mean'] <= temp_range[1])
]

### METRICAS PRINCIPALES
st.header("📊 Metricas Generales")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Distritos Analizados", f"{len(filtered_df):,}")

with col2:
    temp_mean = filtered_df['mean'].mean()
    st.metric("Temperatura Media", f"{temp_mean:.2f}°C")

with col3:
    high_risk = len(filtered_df[filtered_df['risk_category'].isin(['High', 'Very High'])])
    st.metric("Distritos Alto Riesgo", f"{high_risk:,}")

with col4:
    temp_min = filtered_df['min'].min()
    st.metric("Temperatura Minima", f"{temp_min:.2f}°C")

st.divider()

### TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Visualizaciones", 
    "📋 Datos", 
    "🗺️ Mapas", 
    "📜 Politicas Publicas"
])

### TAB 1: VISUALIZACIONES
with tab1:
    st.header("Visualizaciones de Temperatura")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Distribucion de Temperatura Media")
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.hist(filtered_df['mean'], bins=30, color='steelblue', edgecolor='black', alpha=0.7)
        ax.axvline(filtered_df['mean'].mean(), color='red', linestyle='--', label='Media')
        ax.set_xlabel('Temperatura Media (°C)')
        ax.set_ylabel('Frecuencia')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
    
    with col2:
        st.subheader("Distribucion por Categoria de Riesgo")
        risk_counts = filtered_df['risk_category'].value_counts()
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = {'Very High': '#d62728', 'High': '#ff7f0e', 'Moderate': '#ffbb78', 'Low': '#2ca02c'}
        ax.bar(risk_counts.index, risk_counts.values, 
               color=[colors.get(x, 'gray') for x in risk_counts.index],
               edgecolor='black')
        ax.set_xlabel('Categoria de Riesgo')
        ax.set_ylabel('Numero de Distritos')
        ax.grid(True, alpha=0.3, axis='y')
        st.pyplot(fig)
    
    st.subheader("Top 15 Distritos Mas Frios")
    top15 = filtered_df.nsmallest(15, 'mean')[['NAME', 'REGION', 'mean', 'risk_category']]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(15), top15['mean'], color='darkblue', edgecolor='black')
    ax.set_yticks(range(15))
    ax.set_yticklabels(top15['NAME'].str[:30], fontsize=9)
    ax.set_xlabel('Temperatura Media (°C)')
    ax.set_title('Top 15 Distritos con Menor Temperatura')
    ax.invert_yaxis()
    ax.grid(True, alpha=0.3, axis='x')
    st.pyplot(fig)

### TAB 2: DATOS
with tab2:
    st.header("Tabla de Estadisticas Zonales")
    
    ### Mostrar datos filtrados
    display_cols = ['NAME', 'REGION', 'mean', 'min', 'max', 'std', 'p10', 'p90', 
                    'frost_risk_index', 'risk_category']
    
    st.dataframe(
        filtered_df[display_cols].sort_values('frost_risk_index', ascending=False),
        use_container_width=True,
        height=400
    )
    
    ### Descargar datos
    csv = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name='estadisticas_heladas.csv',
        mime='text/csv'
    )
    
    ### Estadisticas resumen
    st.subheader("Estadisticas Resumidas")
    
    summary_stats = filtered_df[['mean', 'min', 'max', 'std', 'frost_risk_index']].describe()
    st.dataframe(summary_stats, use_container_width=True)

### TAB 3: MAPAS
with tab3:
    st.header("Mapas Coropleticos")
    
    ### Merge para visualizacion
    map_data = districts_gdf.merge(
        filtered_df[['UBIGEO', 'mean', 'frost_risk_index', 'risk_category']], 
        on='UBIGEO', 
        how='inner'
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Temperatura Media por Distrito")
        fig, ax = plt.subplots(figsize=(10, 8))
        map_data.plot(
            column='mean',
            cmap='RdYlBu_r',
            legend=True,
            edgecolor='black',
            linewidth=0.2,
            ax=ax
        )
        ax.set_title('Temperatura Media (°C)')
        ax.axis('off')
        st.pyplot(fig)
    
    with col2:
        st.subheader("Indice de Riesgo de Heladas")
        fig, ax = plt.subplots(figsize=(10, 8))
        map_data.plot(
            column='frost_risk_index',
            cmap='YlOrRd',
            legend=True,
            edgecolor='black',
            linewidth=0.2,
            ax=ax
        )
        ax.set_title('Indice de Riesgo de Heladas')
        ax.axis('off')
        st.pyplot(fig)

### TAB 4: POLITICAS PUBLICAS
with tab4:
    st.header("📜 Propuestas de Politicas Publicas")
    
    ### Resumen ejecutivo
    st.subheader("Resumen Ejecutivo")
    
    total_budget = policies_df['costo_total_s'].sum()
    total_beneficiaries = policies_df['beneficiarios'].sum()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Presupuesto Total", f"S/ {total_budget:,.0f}")
    
    with col2:
        st.metric("Beneficiarios", f"{total_beneficiaries:,}")
    
    with col3:
        st.metric("Propuestas", f"{len(policies_df)}")
    
    st.divider()
    
    ### Mostrar propuestas
    for idx, row in policies_df.iterrows():
        with st.expander(f"**{row['propuesta']}**"):
            st.write(f"**Objetivo:** {row['objetivo']}")
            st.write(f"**Poblacion Objetivo:** {row['poblacion_objetivo']}")
            st.write(f"**Intervencion:** {row['intervencion']}")
            st.write(f"**Costo Unitario:** S/ {row['costo_unitario_s']:,.0f}")
            st.write(f"**Cobertura:** {row['cobertura_pct']:.0f}%")
            st.write(f"**Beneficiarios:** {row['beneficiarios']:,}")
            st.write(f"**Presupuesto Total:** S/ {row['costo_total_s']:,.0f}")
            st.write(f"**KPIs:** {row['kpi']}")
            st.write(f"**Plazo:** {row['plazo_años']} años")
    
    ### Grafico de presupuesto
    st.subheader("Distribucion de Presupuesto")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(range(len(policies_df)), policies_df['costo_total_s'] / 1e6, 
           color=['steelblue', 'orange', 'green'], edgecolor='black')
    ax.set_xticks(range(len(policies_df)))
    ax.set_xticklabels(policies_df['propuesta'].str[:30], rotation=15, ha='right')
    ax.set_ylabel('Presupuesto (Millones de Soles)')
    ax.set_title('Presupuesto por Propuesta')
    ax.grid(True, alpha=0.3, axis='y')
    st.pyplot(fig)
    
    ### Descargar documento completo
    policy_doc_path = DATA_DIR / 'outputs' / 'POLICY_PROPOSALS.md'
    if policy_doc_path.exists():
        with open(policy_doc_path, 'r', encoding='utf-8') as f:
            policy_text = f.read()
        
        st.download_button(
            label="📄 Descargar Documento Completo (Markdown)",
            data=policy_text,
            file_name='POLICY_PROPOSALS.md',
            mime='text/markdown'
        )

### FOOTER
st.divider()
st.caption("Analisis de Riesgo de Heladas en Peru - Temperatura Minima (Tmin)")
st.caption("Fuente: Datos geoespaciales de temperatura por distrito")