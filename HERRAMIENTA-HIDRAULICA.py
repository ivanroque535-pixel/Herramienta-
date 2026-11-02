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
    
    # Cálculo de densidad y viscosidad según la temperatura
    rho_agua = 1000.0 - (temp_agua - 4)**2 / 180.0  # kg/m³
    nu_agua = (1.787 / (1 + 0.0337 * temp_agua + 0.000221 * (temp_agua**2))) * 1e-6  # m²/s
    
    st.caption(f"**Densidad (ρ):** {rho_agua:.2f} kg/m³")
    st.caption(f"**Viscosidad cinemática (ν):** {nu_agua*1e6:.4f} ×10⁻⁶ m²/s")
    
    st.divider()
    
    st.subheader("2. Criterios Operativos y Red")
    p_min_requerida = st.number_input("Presión mínima requerida en mueble (m.c.a.)", min_value=0.5, value=2.0, step=0.5)
    desnivel_topografico = st.number_input("Desnivel topográfico total ΔZ (m)", min_value=0.0, value=5.20, step=0.10)
    
    st.divider()
    
    st.subheader("3. Parámetros Electromecánicos")
    eficiencia_bomba = st.slider("Eficiencia de la bomba (η)", min_value=0.40, max_value=0.85, value=0.60, step=0.05)

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
# PESTAÑA 1: ENTRADA DE DATOS Y SIMULTANEIDAD (MÓDULO 1)
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
    
    if "CPVC" in material_predeterminado or "Cobre" in material_predeterminado or "PVC" in material_predeterminado:
        eps_default = 0.0015  # mm
        c_default = 150
    else:
        eps_default = 0.15    # mm
        c_default = 120

    st.markdown("### 🛠️ Tabla de Configuración de Tramos")
    st.caption("Puedes modificar directamente los datos de la tabla (longitudes, muebles, diámetros, accesorios).")

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

    def calcular_gasto_hunter(um):
        if um <= 0:
            return 0.0
        elif um <= 10:
            return 0.12 * (um ** 0.65)
        elif um <= 50:
            return 0.25 * (um ** 0.45)
        else:
            return 0.40 * (um ** 0.38)

    df_procesado = df_tramos.copy()
    df_procesado["Rugosidad_mm"] = eps_default
    df_procesado["Coef_C"] = c_default
    
    if "Hunter" in metodo_simultaneidad:
        df_procesado["Q_diseno_Lps"] = df_procesado["UM"].apply(calcular_gasto_hunter)
    elif "ks" in metodo_simultaneidad:
        df_procesado["n_muebles"] = df_procesado["UM"].apply(lambda x: max(1, x))
        df_procesado["ks"] = df_procesado["n_muebles"].apply(lambda n: 1.0 if n <= 1 else 1.0 / np.sqrt(n - 1))
        df_procesado["Q_diseno_Lps"] = df_procesado["n_muebles"] * 0.15 * df_procesado["ks"]
    else:
        df_procesado["Q_diseno_Lps"] = df_procesado["Q_directo_Lps"]

    df_procesado["Q_diseno_m3s"] = df_procesado["Q_diseno_Lps"] / 1000.0
    df_procesado["Area_m2"] = np.pi * ((df_procesado["DN_mm"] / 1000.0) ** 2) / 4.0
    df_procesado["Velocidad_ms"] = df_procesado["Q_diseno_m3s"] / df_procesado["Area_m2"]

    st.session_state["df_hidraulica"] = df_procesado
    st.success(f"✅ Tramos procesados exitosamente ({len(df_procesado)} tramos registrados). Procede a la Pestaña 2 para la evaluación de pérdidas.")

# ------------------------------------------------------------------------------
# PESTAÑA 2: EVALUACIÓN DUAL DE PÉRDIDAS POR FRICCIÓN (MÓDULO 2)
# ------------------------------------------------------------------------------
with tab2:
    st.header("⚖️ Módulo 2: Pérdidas por Fricción y Pérdidas Menores")
    
    if "df_hidraulica" not in st.session_state:
        st.warning("⚠️ Primero debes ingresar y procesar los tramos en la Pestaña 1.")
    else:
        df_mod2 = st.session_state["df_hidraulica"].copy()
        g = 9.81  # m/s²

        # Funciones de cálculo hidráulico
        def factor_friccion_swamee_jain(re, eps_m, d_m):
            """Calcula el factor de fricción f usando Swamee-Jain (Colebrook-White aprox)"""
            if re < 2300:
                return 64.0 / re if re > 0 else 0.0  # Flujo laminar
            else:
                denom = np.log10((eps_m / (3.7 * d_m)) + (5.74 / (re ** 0.9)))
                return 0.25 / (denom ** 2)

        # Vectorización de cálculos por tramo
        Re_list = []
        f_list = []
        hf_darcy_list = []
        hf_hw_list = []
        hm_list = []
        htotal_darcy_list = []
        alerta_v_list = []

        for idx, row in df_mod2.iterrows():
            L = row["L_m"]
            D_m = row["DN_mm"] / 1000.0
            v = row["Velocidad_ms"]
            Q_m3s = row["Q_diseno_m3s"]
            eps_m = row["Rugosidad_mm"] / 1000.0
            C = row["Coef_C"]
            K_acc = row["Acc_K_total"]

            # Reynolds
            Re = (v * D_m) / nu_agua if nu_agua > 0 else 0.0
            Re_list.append(Re)

            # Factor f (Darcy)
            f = factor_friccion_swamee_jain(Re, eps_m, D_m)
            f_list.append(f)

            # Pérdida por fricción Darcy-Weisbach (m)
            hf_darcy = f * (L / D_m) * ((v ** 2) / (2 * g)) if D_m > 0 else 0.0
            hf_darcy_list.append(hf_darcy)

            # Pérdida por fricción Hazen-Williams (m)
            if D_m > 0 and C > 0:
                hf_hw = 10.674 * L * (Q_m3s ** 1.852) / ((C ** 1.852) * (D_m ** 4.871))
            else:
                hf_hw = 0.0
            hf_hw_list.append(hf_hw)

            # Pérdidas menores hm (m)
            hm = K_acc * ((v ** 2) / (2 * g))
            hm_list.append(hm)

            # Pérdida total por tramo (Darcy + hm)
            htotal_darcy_list.append(hf_darcy + hm)

            # Verificación de velocidad normativa
            if v < 0.60:
                alerta_v_list.append("⚠️ Baja (< 0.6 m/s)")
            elif v > 2.50:
                alerta_v_list.append("🚨 Alta (> 2.5 m/s)")
            else:
                alerta_v_list.append("✅ Ok (0.6 - 2.5 m/s)")

        # Agregar columnas calculadas al DataFrame
        df_mod2["Re"] = Re_list
        df_mod2["Factor_f"] = f_list
        df_mod2["hf_Darcy_m"] = hf_darcy_list
        df_mod2["hf_HW_m"] = hf_hw_list
        df_mod2["hm_Acc_m"] = hm_list
        df_mod2["h_Total_Tramo_m"] = htotal_darcy_list
        df_mod2["Estado_Velocidad"] = alerta_v_list

        # Actualizar estado global de la app
        st.session_state["df_hidraulica"] = df_mod2

        # Despliegue de métricas resumidas
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Pérdida Fricción Total (Darcy)", f"{df_mod2['hf_Darcy_m'].sum():.3f} m")
        col_m2.metric("Pérdida Fricción Total (Hazen-Williams)", f"{df_mod2['hf_HW_m'].sum():.3f} m")
        col_m3.metric("Diferencia Relativa Promedio", f"{abs(df_mod2['hf_Darcy_m'].sum() - df_mod2['hf_HW_m'].sum()) / df_mod2['hf_Darcy_m'].sum() * 100:.2f} %")

        st.subheader("📊 Tabla Comparativa de Resultados Hidráulicos por Tramo")
        
        # Selección de columnas visibles ordenadas para presentación ejecutiva
        columnas_ver = [
            "Tramo", "Q_diseno_Lps", "Velocidad_ms", "Estado_Velocidad", 
            "Re", "Factor_f", "hf_Darcy_m", "hf_HW_m", "hm_Acc_m", "h_Total_Tramo_m"
        ]
        
        st.dataframe(
            df_mod2[columnas_ver].style.format({
                "Q_diseno_Lps": "{:.3f}",
                "Velocidad_ms": "{:.2f}",
                "Re": "{:,.0f}",
                "Factor_f": "{:.4f}",
                "hf_Darcy_m": "{:.3f}",
                "hf_HW_m": "{:.3f}",
                "hm_Acc_m": "{:.3f}",
                "h_Total_Tramo_m": "{:.3f}"
            }),
            use_container_width=True
        )

        st.success("✅ Evaluación dual realizada. Procede a la Pestaña 3 para determinar la Ruta Crítica y CDT.")

# ------------------------------------------------------------------------------
# PESTAÑA 3: RUTA CRÍTICA Y CARGA DINÁMICA TOTAL
# ------------------------------------------------------------------------------
with tab3:
    st.header("Acumulación de Presión y Punto Desfavorable")
    st.info("Identificación automática de la ruta crítica y cálculo global de pérdidas acumuladas.")

# ------------------------------------------------------------------------------
# PESTAÑA 4: EQUIPO DE BOMBEO Y GRÁFICOS INTERACTIVOS
# ------------------------------------------------------------------------------
with tab4:
    st.header("Dimensionamiento de Bomba y Análisis Gráfico")
    st.info("Potencia requerida (HP), curvas del sistema vs. bomba y análisis transitorio de golpe de ariete.")

# ------------------------------------------------------------------------------
# PESTAÑA 5: MEMORIA DE CÁLCULO Y AUDITORÍA DE IA
# ------------------------------------------------------------------------------
with tab5:
    st.header("Memoria Ejecutiva y Bitácora de Prompts")
    st.info("Generación de reporte técnico ejecutable y registro de auditoría/control de alucinaciones.")
    
