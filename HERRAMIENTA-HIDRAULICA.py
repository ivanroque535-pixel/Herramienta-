import streamlit as st
import pandas as pd
import numpy as np

# ==============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILOS
# ==============================================================================
st.set_page_config(
    page_title="HIDRA-NET PRO | Análisis Hidráulico UAA",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados para UI profesional
st.markdown("""
    <style>
    .main-header {
        font-size: 2.2rem;
        color: #1E3A8A;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #2563EB;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💧 HIDRA-NET PRO: Redes de Agua Potable y Bombeo</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Universidad Autónoma de Aguascalientes | Instalaciones Básicas</div>', unsafe_allow_html=True)

# ==============================================================================
# 2. BARRA LATERAL (SIDEBAR) - INSUMOS Y PARÁMETROS GLOBALES
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/water-pipe.png", width=80)
    st.header("⚙️ Parámetros Globales")
    
    st.subheader("1. Propiedades del Fluido (Agua)")
    temp_agua = st.slider("Temperatura del agua (°C)", min_value=5, max_value=40, value=20, step=1)
    
    # Cálculo aproximado de densidad y viscosidad según la temperatura
    rho_agua = 1000.0 - (temp_agua - 4)**2 / 180.0  # kg/m³
    nu_agua = (1.787 / (1 + 0.0337 * temp_agua + 0.000221 * (temp_agua**2))) * 1e-6  # m²/s
    
    st.caption(f"**Densidad (ρ):** {rho_agua:.2f} kg/m³")
    st.caption(f"**Viscosidad cinemática (ν):** {nu_agua*1e6:.4f} ×10⁻⁶ m²/s")
    
    st.divider()
    
    st.subheader("2. Criterios Operativos y Red")
    p_min_requerida = st.number_input("Presión mínima requerida en mueble (m.c.a.)", min_value=0.5, value=2.0, step=0.5)[cite: 2, 3]
    desnivel_topografico = st.number_input("Desnivel topográfico total ΔZ (m)", min_value=0.0, value=5.20, step=0.10)[cite: 2, 3]
    
    st.divider()
    
    st.subheader("3. Parámetros Electromecánicos")
    eficiencia_bomba = st.slider("Eficiencia de la bomba (η)", min_value=0.40, max_value=0.85, value=0.60, step=0.05)[cite: 3, 5]

# ==============================================================================
# 3. NAVEGACIÓN EN PESTAÑAS (ST.TABS)
# ==============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📋 1. Red & Simultaneidad",
    "⚖️ 2. Pérdidas Darcy vs Hazen",
    "🗺️ 3. Ruta Crítica & CDT",
    "⚡ 4. Bomba & Gráficos",
    "📄 5. Memoria & Auditoría IA"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: ENTRADA DE DATOS Y SIMULTANEIDAD
# ------------------------------------------------------------------------------
with tab1:
    st.header("Entrada de Tramos de Tubería y Gastos")
    st.info("Ingresa los datos topológicos de los tramos, accesorios, diámetros y demandas sanitarias.")
    # Estructura del formulario editable para el Módulo 1 (se implementará en la Fase 3)

# ------------------------------------------------------------------------------
# PESTAÑA 2: EVALUACIÓN DUAL DE PÉRDIDAS POR FRICCIÓN
# ------------------------------------------------------------------------------
with tab2:
    st.header("Comparativa Simultánea: Darcy-Weisbach vs. Hazen-Williams")
    st.info("Cálculo paralelo del factor de fricción (Colebrook-White/Swamee-Jain) y ecuación empírica de Hazen-Williams.")[cite: 2]

# ------------------------------------------------------------------------------
# PESTAÑA 3: RUTA CRÍTICA Y CARGA DINÁMICA TOTAL
# ------------------------------------------------------------------------------
with tab3:
    st.header("Acumulación de Presión y Punto Desfavorable")
    st.info("Identificación automática de la ruta crítica y cálculo global de pérdidas acumuladas.")[cite: 2]

# ------------------------------------------------------------------------------
# PESTAÑA 4: EQUIPO DE BOMBEO Y GRÁFICOS INTERACTIVOS
# ------------------------------------------------------------------------------
with tab4:
    st.header("Dimensionamiento de Bomba y Análisis Gráfico")
    st.info("Potencia requerida (HP), curvas del sistema vs. bomba y análisis transitorio de golpe de ariete.")[cite: 2, 3, 5]

# ------------------------------------------------------------------------------
# PESTAÑA 5: MEMORIA DE CÁLCULO Y AUDITORÍA DE IA
# ------------------------------------------------------------------------------
with tab5:
    st.header("Memoria Ejecutiva y Bitácora de Prompts")
    st.info("Generación de reporte técnico ejecutable y registro de auditoría/control de alucinaciones.")[cite: 2, 3, 4]
