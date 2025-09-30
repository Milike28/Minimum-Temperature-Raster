"""
Dashboard de Análisis de Heladas en Perú
Análisis de Temperatura Mínima (Tmin) por Distrito
"""
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image

# ══════════════════════════════════════════════════════════════
# CONFIGURACIÓN
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Análisis Heladas Perú",
    page_icon="❄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Rutas relativas (funciona en Windows Y Linux)
BASE_DIR = Path(__file__).parent.parent
TABLES = BASE_DIR / 'data' / 'outputs' / 'tables'
PLOTS = BASE_DIR / 'data' / 'outputs' / 'plots'

# ══════════════════════════════════════════════════════════════
# CARGAR DATOS
# ══════════════════════════════════════════════════════════════
@st.cache_data
def load_data():
    """Carga tablas CSV y cachea resultados"""
    return (
        pd.read_csv(TABLES / 'zonal_statistics.csv'),
        pd.read_csv(TABLES / 'policy_proposals.csv')
    )

@st.cache_data
def load_image(path):
    """Carga imágenes pre-generadas"""
    return Image.open(path)

stats, policies = load_data()

# ══════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════
st.title("❄️ Análisis de Riesgo de Heladas en Perú")
st.markdown("**Análisis Espacial de Temperatura Mínima (Tmin) por Distrito**")
st.markdown("---")

# ══════════════════════════════════════════════════════════════
# SIDEBAR FILTROS
# ══════════════════════════════════════════════════════════════
st.sidebar.header("🔍 Filtros")

regions = ['Todos'] + sorted(stats['REGION'].unique().tolist())
sel_region = st.sidebar.selectbox("📍 Región", regions)

risk_cats = ['Todos'] + sorted(stats['risk_category'].unique().tolist())
sel_risk = st.sidebar.selectbox("⚠️ Categoría de Riesgo", risk_cats)

temp_range = st.sidebar.slider(
    "🌡️ Temperatura Media (°C)",
    float(stats['mean'].min()),
    float(stats['mean'].max()),
    (float(stats['mean'].min()), float(stats['mean'].max()))
)

# Aplicar filtros
df = stats.copy()
if sel_region != 'Todos':
    df = df[df['REGION'] == sel_region]
if sel_risk != 'Todos':
    df = df[df['risk_category'] == sel_risk]
df = df[(df['mean'] >= temp_range[0]) & (df['mean'] <= temp_range[1])]

# ══════════════════════════════════════════════════════════════
# MÉTRICAS PRINCIPALES
# ══════════════════════════════════════════════════════════════
st.header("📊 Métricas Clave")
c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Distritos", f"{len(df):,}")
c2.metric("Temp Media", f"{df['mean'].mean():.2f}°C")
c3.metric("Alto Riesgo", f"{len(df[df['risk_category'].isin(['High','Very High'])]):,}")
c4.metric("Temp Mínima", f"{df['min'].min():.2f}°C")
c5.metric("Desv. Estándar", f"{df['std'].mean():.2f}°C")

st.markdown("---")

# ══════════════════════════════════════════════════════════════
# TABS PRINCIPALES
# ══════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Visualizaciones",
    "🗺️ Mapas",
    "📋 Datos Detallados",
    "📜 Políticas Públicas",
    "📖 Metodología"
])

# ──────────────────────────────────────────────────────────────
# TAB 1: VISUALIZACIONES
# ──────────────────────────────────────────────────────────────
with tab1:
    st.header("Análisis Visual de Temperatura")
    if sel_region != 'Todos':
        st.subheader(f"Distribución de Temperatura en {sel_region}")
    else:
        st.subheader("Distribución de Temperatura en todas las Regiones")
    # Gráfico 1: Distribución de temperatura
    st.subheader("1️⃣ Distribución de Temperatura Media")
    if (PLOTS / '01_temperature_distribution.png').exists():
        st.image(load_image(PLOTS / '01_temperature_distribution.png'), 
                 use_container_width=True)
    else:
        fig, ax = plt.subplots(figsize=(10,5))
        ax.hist(df['mean'], bins=30, color='steelblue', edgecolor='black')
        ax.axvline(df['mean'].mean(), color='red', linestyle='--', label=f'Media: {df["mean"].mean():.2f}°C')
        ax.set_xlabel('Temperatura Media (°C)')
        ax.set_ylabel('Frecuencia')
        ax.legend()
        ax.grid(alpha=0.3)
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Gráfico 2: Ranking de distritos
    st.subheader("2️⃣ Ranking de Distritos Más Fríos (Top 15)")
    if (PLOTS / '02_temperature_ranking.png').exists():
        st.image(load_image(PLOTS / '02_temperature_ranking.png'), 
                 use_container_width=True)
    else:
        top15 = df.nsmallest(15, 'mean')
        fig, ax = plt.subplots(figsize=(10,6))
        ax.barh(range(15), top15['mean'], color='darkblue', edgecolor='black')
        ax.set_yticks(range(15))
        ax.set_yticklabels(top15['NAME'].str[:30])
        ax.set_xlabel('Temperatura Media (°C)')
        ax.invert_yaxis()
        ax.grid(alpha=0.3, axis='x')
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Gráfico 3: Temperatura por región
    st.subheader("3️⃣ Temperatura Media por Región")
    if (PLOTS / '04_temperature_by_region.png').exists():
        st.image(load_image(PLOTS / '04_temperature_by_region.png'), 
                 use_container_width=True)
    else:
        region_stats = df.groupby('REGION')['mean'].agg(['mean', 'std']).sort_values('mean')
        fig, ax = plt.subplots(figsize=(10,6))
        ax.barh(region_stats.index, region_stats['mean'], xerr=region_stats['std'],
                color='coral', edgecolor='black', capsize=3)
        ax.set_xlabel('Temperatura Media (°C)')
        ax.grid(alpha=0.3, axis='x')
        st.pyplot(fig)
    
    st.markdown("---")
    
    # Gráfico 4: Categorías de riesgo
    st.subheader("4️⃣ Distribución por Categoría de Riesgo")
    col1, col2 = st.columns(2)
    
    with col1:
        risk_counts = df['risk_category'].value_counts()
        fig, ax = plt.subplots(figsize=(8,5))
        colors = {'Very High': '#d62728', 'High': '#ff7f0e', 'Moderate': '#ffbb78', 'Low': '#2ca02c'}
        ax.bar(risk_counts.index, risk_counts.values,
               color=[colors.get(x, 'gray') for x in risk_counts.index],
               edgecolor='black')
        ax.set_ylabel('Número de Distritos')
        ax.grid(alpha=0.3, axis='y')
        st.pyplot(fig)
    
    with col2:
        st.dataframe(
            df['risk_category'].value_counts().reset_index()
            .rename(columns={'count': 'Cantidad', 'risk_category': 'Categoría'}),
            use_container_width=True
        )

# ──────────────────────────────────────────────────────────────
# TAB 2: MAPAS
# ──────────────────────────────────────────────────────────────
with tab2:
    st.header("🗺️ Mapas Coroplécticos")
    
    st.subheader("Visualización Espacial de Temperatura")
    if (PLOTS / '03_choropleth_maps.png').exists():
        st.image(load_image(PLOTS / '03_choropleth_maps.png'), 
                 use_container_width=True,
                 caption="Izquierda: Temperatura Media | Derecha: Índice de Riesgo de Heladas")
    else:
        st.info("📌 Los mapas coroplécticos fueron generados en el análisis previo. Ejecuta el notebook de análisis para generarlos.")
    
    st.markdown("---")
    st.markdown("""
    **Interpretación:**
    - **Azul intenso**: Zonas con temperaturas muy bajas (alto riesgo)
    - **Rojo**: Zonas con temperaturas moderadas/altas (bajo riesgo)
    - Los distritos andinos muestran mayor vulnerabilidad a heladas
    """)

# ──────────────────────────────────────────────────────────────
# TAB 3: DATOS DETALLADOS
# ──────────────────────────────────────────────────────────────
with tab3:
    st.header("📋 Tabla de Estadísticas Zonales")
    
    # Estadísticas resumidas
    st.subheader("📊 Resumen Estadístico")
    summary = df[['mean', 'min', 'max', 'std', 'p10', 'p90', 'frost_risk_index']].describe()
    st.dataframe(summary, use_container_width=True)
    
    st.markdown("---")
    
    # Tabla completa
    st.subheader("📄 Datos Completos por Distrito")
    cols = ['NAME', 'REGION', 'mean', 'min', 'max', 'std', 'p10', 'p90', 
            'frost_risk_index', 'risk_category']
    
    st.dataframe(
        df[cols].sort_values('frost_risk_index', ascending=False).reset_index(drop=True),
        use_container_width=True,
        height=400
    )
    
    # Descarga
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Descargar CSV Completo",
        csv,
        "estadisticas_heladas_peru.csv",
        "text/csv"
    )

# ──────────────────────────────────────────────────────────────
# TAB 4: POLÍTICAS PÚBLICAS
# ──────────────────────────────────────────────────────────────
with tab4:
    st.header("📜 Propuestas de Políticas Públicas")
    
    # Resumen Ejecutivo
    st.subheader("💼 Resumen Ejecutivo")
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 Presupuesto Total", f"S/ {policies['costo_total_s'].sum():,.0f}")
    c2.metric("👥 Beneficiarios", f"{policies['beneficiarios'].sum():,}")
    c3.metric("📋 Propuestas", f"{len(policies)}")
    
    st.markdown("---")
    
    # Diagnóstico
    st.subheader("🔍 Diagnóstico")
    high_risk_districts = len(stats[stats['risk_category'].isin(['High', 'Very High'])])
    total_districts = len(stats)
    
    st.markdown(f"""
    **Situación Actual:**
    - **{high_risk_districts:,} distritos** ({high_risk_districts/total_districts*100:.1f}%) en categorías de **Alto y Muy Alto Riesgo**
    - Temperatura mínima absoluta registrada: **{stats['min'].min():.2f}°C**
    - Promedio nacional de temperatura mínima: **{stats['mean'].mean():.2f}°C**
    - Desviación estándar promedio: **{stats['std'].mean():.2f}°C**
    
    **Áreas Críticas Identificadas:**
    1. **Zona Andina Central y Sur**: Mayor vulnerabilidad
    2. **Distritos de altura (>3500 msnm)**: Temperaturas extremas frecuentes
    3. **Población rural dispersa**: Menor capacidad de respuesta
    """)
    
    st.markdown("---")
    
    # Propuestas detalladas
    st.subheader("🎯 Medidas Prioritarias")
    
    for i, (_, r) in enumerate(policies.iterrows(), 1):
        with st.expander(f"**Propuesta {i}: {r['propuesta']}**", expanded=(i==1)):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"**🎯 Objetivo:** {r['objetivo']}")
                st.markdown(f"**👥 Población Objetivo:** {r['poblacion_objetivo']}")
                st.markdown(f"**🔧 Intervención:** {r['intervencion']}")
                st.markdown(f"**📊 KPIs:** {r['kpi']}")
                st.markdown(f"**⏱️ Plazo:** {r['plazo_años']} años")
            
            with col2:
                st.metric("💰 Costo Total", f"S/ {r['costo_total_s']:,.0f}")
                st.metric("📦 Costo Unitario", f"S/ {r['costo_unitario_s']:,.0f}")
                st.metric("👥 Beneficiarios", f"{r['beneficiarios']:,}")
                st.metric("📈 Cobertura", f"{r['cobertura_pct']:.0f}%")
    
    st.markdown("---")
    
    # Gráfico de presupuesto
    st.subheader("💵 Distribución de Presupuesto")
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(range(len(policies)), policies['costo_total_s'] / 1e6,
           color=['#1f77b4', '#ff7f0e', '#2ca02c'], edgecolor='black')
    ax.set_xticks(range(len(policies)))
    ax.set_xticklabels([p[:25] + '...' for p in policies['propuesta']], rotation=20, ha='right')
    ax.set_ylabel('Presupuesto (Millones S/)')
    ax.grid(alpha=0.3, axis='y')
    st.pyplot(fig)

# ──────────────────────────────────────────────────────────────
# TAB 5: METODOLOGÍA
# ──────────────────────────────────────────────────────────────
with tab5:
    st.header("📖 Metodología y Fuentes")
    
    st.subheader("🔬 Métricas Calculadas")
    st.markdown("""
    **Estadísticas Zonales (por distrito):**
    1. **mean**: Temperatura media
    2. **min**: Temperatura mínima absoluta
    3. **max**: Temperatura máxima
    4. **std**: Desviación estándar
    5. **p10**: Percentil 10
    6. **p90**: Percentil 90
    7. **frost_risk_index** (métrica custom): Índice compuesto basado en:
       - Temperatura media
       - Frecuencia de temperaturas extremas
       - Variabilidad (std)
    
    **Categorización de Riesgo:**
    - **Very High**: Temperatura < 5°C
    - **High**: 5°C ≤ Temperatura < 10°C
    - **Moderate**: 10°C ≤ Temperatura < 15°C
    - **Low**: Temperatura ≥ 15°C
    """)
    
    st.subheader("📚 Fuentes de Datos")
    st.markdown("""
    - **Datos Raster**: Temperatura mínima (Tmin) de [fuente específica]
    - **Límites Administrativos**: INEI - Perú
    - **Procesamiento**: `rasterstats`, `rioxarray`, `geopandas`
    - **Sistema de Coordenadas**: EPSG:4326 (WGS 84)
    """)
    
    st.subheader("⚙️ Tecnologías Utilizadas")
    st.code("""
    - Python 3.13
    - Streamlit 1.28+
    - pandas 2.2+
    - matplotlib 3.8+
    - GeoPandas (análisis offline)
    - rasterstats (zonal statistics)
    """, language="python")

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("---")
st.caption("🌡️ Análisis de Riesgo de Heladas en Perú | Fuente: Datos Raster de Temperatura Mínima")
st.caption("📊 Dashboard desarrollado con Streamlit | Datos procesados con GeoPandas y rasterstats")