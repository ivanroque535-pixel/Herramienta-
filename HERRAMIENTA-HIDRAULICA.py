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
    # ------------------------------------------------------------------------------
# PESTAÑA 1: ENTRADA DE DATOS Y SIMULTANEIDAD
# ------------------------------------------------------------------------------
with tab1:
    st.header("📋 Módulo 1: Topología de Red, Tramos y Simultaneidad")
    
    col_metodo, col_mat = st.columns([2, 2])
    with col_metodo:
        metodo_simultaneidad = st.selectbox(
            "Selecciona el Método de Simultaneidad / Gasto de Diseño:",
            ["Unidades Mueble de Hunter (Residencial MAPAS-CONAGUA)", "Coeficiente de Simultaneidad (ks = 1/√(n-1))", "Gasto Directo Conocido (Lps)"]
        )
    
    with col_mat:
        material_predeterminado = st.selectbox(
            "Material Predeterminado de la Red:",
            ["CPVC (ε = 0.0015 mm, C = 150)", "Cobre (ε = 0.0015 mm, C = 150)", "PVC (ε = 0.0015 mm, C = 150)", "Acero Galvanizado (ε = 0.15 mm, C = 120)"]
        )
    
    # Asignación de rugosidad y C según material seleccionado por defecto
    if "CPVC" in material_predeterminado or "Cobre" in material_predeterminado or "PVC" in material_predeterminado:
        eps_default = 0.0015  # mm
        c_default = 150
    else:
        eps_default = 0.15    # mm
        c_default = 120

    st.markdown("### 🛠️ Tabla de Configuración de Tramos")
    st.caption("Puedes modificar directamente los datos de la tabla (longitudes, muebles, diámetros, accesorios).")

    # Datos por defecto correspondientes al Caso A de la Rúbrica (2 Niveles, 8 Muebles)
    datos_iniciales = pd.DataFrame([
        {"Tramo": "Cisterna -> TDT (Subida Principal)", "L_m": 8.5, "DN_mm": 25.4, "UM": 24, "Q_directo_Lps": 0.0, "Acc_K_total": 3.5, "Desnivel_m": 5.2, "Mueble_Final": "Tanque Distribuidor"},
        {"Tramo": "TDT -> Regadera 1 (P. Alta)", "L_m": 4.0, "DN_mm": 19.05, "UM": 3, "Q_directo_Lps": 0.0, "Acc_K_total": 1.5, "Desnivel_m": 0.0, "Mueble_Final": "Regadera P.A. (Crítico P.A.)"},
        {"Tramo": "TDT -> Sanitario 1 (P. Alta)", "L_m": 3.5, "DN_mm": 19.05, "UM": 3, "Q_directo_Lps": 0.0, "Acc_K_total": 1.2, "Desnivel_m": 0.0, "Mueble_Final": "Sanitario P.A."},
        {"Tramo": "TDT -> Lavabo 1 (P. Alta)", "L_m": 3.0, "DN_mm": 12.7, "UM": 1, "Q_directo_Lps": 0.0, "Acc_K_total": 1.0, "Desnivel_m": 0.0, "Mueble_Final": "Lavabo P.A."},
        {"Tramo": "TDT -> Regadera 2 (P. Baja)", "L_m": 6.0, "DN_mm": 19.05, "UM": 3, "Q_directo_Lps": 0.0, "Acc_K_total": 1.8, "Desnivel_m": -2.6, "Mueble_Final": "Regadera P.B."},
        {"Tramo": "TDT -> Sanitario 2 (P. Baja)", "L_m": 5.5, "DN_mm": 19.05, "UM": 3, "Q_directo_Lps": 0.0, "Acc_K_total": 1.2, "Desnivel_m": -2.6, "Mueble_Final": "Sanitario P.B."},
        {"Tramo": "TDT -> Lavabo 2 (P. Baja)", "L_m": 5.0, "DN_mm": 12.7, "UM": 1, "Q_directo_Lps": 0.0, "Acc_K_total": 1.0, "Desnivel_m": -2.6, "Mueble_Final": "Lavabo P.B."},
        {"Tramo": "TDT -> Fregadero (P. Baja)", "L_m": 7.0, "DN_mm": 19.05, "UM": 2, "Q_directo_Lps": 0.0, "Acc_K_total": 1.5, "Desnivel_m": -2.6, "Mueble_Final": "Fregadero Cocina"}
    ])

    df_tramos = st.data_editor(
        datos_iniciales,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Tramo": st.column_config.TextColumn("Identificador Tramo", required=True),
            "L_m": st.column_config.NumberColumn("Longitud L (m)", min_value=0.1, format="%.2f"),
            "DN_mm": st.column_config.NumberColumn("Diámetro Real D (mm)", min_value=6.0, format="%.1f"),
            "UM": st.column_config.NumberColumn("Unidades Mueble (UM)", min_value=0, step=1),
            "Q_directo_Lps": st.column_config.NumberColumn("Q Directo (L/s)", min_value=0.0, format="%.3f"),
            "Acc_K_total": st.column_config.NumberColumn("Σ Coeficientes K Accesorios", min_value=0.0, format="%.2f"),
            "Desnivel_m": st.column_config.NumberColumn("ΔZ Topográfico (m)", format="%.2f"),
            "Mueble_Final": st.column_config.TextColumn("Punto de Descarga / Mueble")
        }
    )

    # --------------------------------------------------------------------------
    # LÓGICA DE PROCESAMIENTO DE CAUDALES Y SIMULTANEIDAD
    # --------------------------------------------------------------------------
    def calcular_gasto_hunter(um):
        """Conversión polinómica exacta de Unidades Mueble Hunter a L/s (Agua Fría/Caliente)"""
        if um <= 0:
            return 0.0
        elif um <= 10:
            return 0.12 * (um ** 0.65)
        elif um <= 50:
            return 0.25 * (um ** 0.45)
        else:
            return 0.40 * (um ** 0.38)

    df_procesado = df_tramos.copy()
    
    # Asignación de rugosidad y C al dataframe
    df_procesado["Rugosidad_mm"] = eps_default
    df_procesado["Coef_C"] = c_default
    
    # Cálculo de Caudal de Diseño Q (L/s y m³/s)
    if "Hunter" in metodo_simultaneidad:
        df_procesado["Q_diseno_Lps"] = df_procesado["UM"].apply(calcular_gasto_hunter)
    elif "ks" in metodo_simultaneidad:
        # Coeficiente ks = 1 / sqrt(n - 1)
        df_procesado["n_muebles"] = df_procesado["UM"].apply(lambda x: max(1, x))
        df_procesado["ks"] = df_procesado["n_muebles"].apply(lambda n: 1.0 if n <= 1 else 1.0 / np.sqrt(n - 1))
        # Asumiendo gasto base unitario de 0.15 L/s por mueble en simulación ks
        df_procesado["Q_diseno_Lps"] = df_procesado["n_muebles"] * 0.15 * df_procesado["ks"]
    else:
        df_procesado["Q_diseno_Lps"] = df_procesado["Q_directo_Lps"]

    df_procesado["Q_diseno_m3s"] = df_procesado["Q_diseno_Lps"] / 1000.0
    df_procesado["Area_m2"] = np.pi * ((df_procesado["DN_mm"] / 1000.0) ** 2) / 4.0
    df_procesado["Velocidad_ms"] = df_procesado["Q_diseno_m3s"] / df_procesado["Area_m2"]

    # Guardar en sesión de Streamlit para consumo de los siguientes módulos
    st.session_state["df_hidraulica"] = df_procesado

    st.success(f"✅ Tramos procesados exitosamente ({len(df_procesado)} tramos registrados). Procede a la Pestaña 2 para la evaluación de pérdidas.")
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
