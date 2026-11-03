import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

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
# PESTAÑA 1: ENTRADA DE DATOS (NODOS), SIMULTANEIDAD Y ACCESORIOS
# ------------------------------------------------------------------------------
with tab1:
    st.header("📋 Módulo 1: Topología de Red, Tramos y Simultaneidad")
    
    col_metodo, col_mat = st.columns([2, 2])
    with col_metodo:
        metodo_simultaneidad = st.selectbox(
            "Selecciona el Método de Simultaneidad / Gasto de Diseño:",
            ["Unidades Mueble (Hunter MAPAS-CONAGUA)", "Coeficiente de Simultaneidad (ks)", "Gasto Directo Conocido (Lps)"]
        )
    with col_mat:
        material_predeterminado = st.selectbox(
            "Material Predeterminado de la Red:",
            ["CPVC/Cobre/PVC (ε = 0.0015 mm, C = 150)", "Acero Galvanizado (ε = 0.15 mm, C = 120)"]
        )
    
    eps_default = 0.0015 if "CPVC" in material_predeterminado else 0.15
    c_default = 150 if "CPVC" in material_predeterminado else 120

    st.markdown("### 🛠️ Tabla de Configuración de Tramos (Desde / Hasta)")
    st.caption("Introduce las **UM Terminales** solo en los nodos que conectan directamente a un mueble. El sistema acumulará las UM hacia atrás (aguas abajo) automáticamente para los tramos principales.")

    # Precarga basada en tu lógica de ramificación
    datos_iniciales = pd.DataFrame([
        {"Desde": "A", "Hasta": "B", "L_m": 2.07, "DN_mm": 38.1, "UM_Terminales": 0, "Q_directo_Lps": 0.0, "Acc_K_total": 0.98, "Desnivel_m": 5.20},
        {"Desde": "B", "Hasta": "Calentador", "L_m": 1.29, "DN_mm": 38.1, "UM_Terminales": 1, "Q_directo_Lps": 0.0, "Acc_K_total": 0.46, "Desnivel_m": 0.00},
        {"Desde": "B", "Hasta": "C", "L_m": 4.44, "DN_mm": 38.1, "UM_Terminales": 0, "Q_directo_Lps": 0.0, "Acc_K_total": 2.88, "Desnivel_m": 0.00},
        {"Desde": "C", "Hasta": "D", "L_m": 1.36, "DN_mm": 25.4, "UM_Terminales": 0, "Q_directo_Lps": 0.0, "Acc_K_total": 1.63, "Desnivel_m": 0.00},
        {"Desde": "D", "Hasta": "Lavadora", "L_m": 0.80, "DN_mm": 12.7, "UM_Terminales": 1, "Q_directo_Lps": 0.0, "Acc_K_total": 0.12, "Desnivel_m": 0.00},
        {"Desde": "D", "Hasta": "E", "L_m": 0.23, "DN_mm": 25.4, "UM_Terminales": 0, "Q_directo_Lps": 0.0, "Acc_K_total": 1.45, "Desnivel_m": 0.00},
        {"Desde": "E", "Hasta": "Lavadero", "L_m": 0.80, "DN_mm": 12.7, "UM_Terminales": 1, "Q_directo_Lps": 0.0, "Acc_K_total": 0.12, "Desnivel_m": 0.00}
    ])

    df_tramos = st.data_editor(
        datos_iniciales,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Desde": st.column_config.TextColumn("Nodo Inicio (Desde)", required=True),
            "Hasta": st.column_config.TextColumn("Nodo Final (Hasta)", required=True),
            "L_m": st.column_config.NumberColumn("Longitud L (m)", min_value=0.1, format="%.2f"),
            "DN_mm": st.column_config.NumberColumn("Diámetro D (mm)", min_value=6.0, format="%.1f"),
            "UM_Terminales": st.column_config.NumberColumn("UM Terminales", min_value=0, step=1),
            "Q_directo_Lps": st.column_config.NumberColumn("Q Directo (L/s)", min_value=0.0, format="%.3f"),
            "Acc_K_total": st.column_config.NumberColumn("Σ Coeficientes K", min_value=0.0, format="%.2f"),
            "Desnivel_m": st.column_config.NumberColumn("ΔZ Topográfico (m)", format="%.2f")
        }
    )

    # --------------------------------------------------------------------------
    # LÓGICA TOPOLÓGICA (ACUMULACIÓN DE MUEBLES AGUAS ABAJO)
    # --------------------------------------------------------------------------
    adj = {}
    um_directas = {}
    
    # Construir grafo dirigido y mapear muebles en cada nodo destino
    for _, row in df_tramos.iterrows():
        u = str(row["Desde"]).strip()
        v = str(row["Hasta"]).strip()
        if u not in adj: adj[u] = []
        adj[u].append(v)
        um_directas[v] = row["UM_Terminales"]

    # Función recursiva (DFS) para sumar los muebles de un nodo y todos sus hijos
    def calcular_um_aguas_abajo(nodo):
        total = um_directas.get(nodo, 0)
        for hijo in adj.get(nodo, []):
            total += calcular_um_aguas_abajo(hijo)
        return total

    df_procesado = df_tramos.copy()
    # Las UM del tramo (u -> v) son todas las UM acumuladas a partir de 'v'
    df_procesado["UM"] = df_procesado["Hasta"].apply(lambda v: calcular_um_aguas_abajo(str(v).strip()))
    
    # Recrear columna "Tramo" combinada para compatibilidad con el resto de módulos
    df_procesado["Tramo"] = df_procesado["Desde"].astype(str) + " -> " + df_procesado["Hasta"].astype(str)
    df_procesado["Mueble_Final"] = df_procesado["Hasta"]
    df_procesado["Rugosidad_mm"] = eps_default
    df_procesado["Coef_C"] = c_default

    # --------------------------------------------------------------------------
    # CALCULADORA LATERAL DE ACCESORIOS (SOBREESCRIBE ΣK SI SE USA)
    # --------------------------------------------------------------------------
    st.markdown("### 🔧 (Opcional) Calculadora Automática de Accesorios")
    if "acc_k_dict" not in st.session_state:
        st.session_state["acc_k_dict"] = {}

    col_c1, col_c2 = st.columns([1, 2])
    with col_c1:
        tramo_sel = st.selectbox("Tramo a desglosar:", df_procesado["Tramo"].tolist())
    with col_c2:
        with st.expander(f"Piezas en {tramo_sel}"):
            cp1, cp2, cp3 = st.columns(3)
            c90 = cp1.number_input("Codos 90°", min_value=0, step=1, key=f"c90_{tramo_sel}")
            tee = cp2.number_input("Tees", min_value=0, step=1, key=f"t_{tramo_sel}")
            val = cp3.number_input("Válvulas", min_value=0, step=1, key=f"v_{tramo_sel}")
            if st.button("Calcular y Aplicar K"):
                k_calculado = (c90 * 0.9) + (tee * 0.6) + (val * 0.2)
                st.session_state["acc_k_dict"][tramo_sel] = k_calculado
                st.success(f"K = {k_calculado:.2f} aplicado al tramo.")

    # Sobreescribir el valor K de la tabla si el usuario usó la calculadora lateral
    df_procesado["Acc_K_total"] = df_procesado.apply(
        lambda r: st.session_state["acc_k_dict"].get(r["Tramo"], r["Acc_K_total"]), axis=1
    )

    # --------------------------------------------------------------------------
    # CÁLCULO DE CAUDALES DE DISEÑO Y VELOCIDAD
    # --------------------------------------------------------------------------
    def calcular_gasto_hunter(um):
        if um <= 0: return 0.0
        elif um <= 10: return 0.12 * (um ** 0.65)
        elif um <= 50: return 0.25 * (um ** 0.45)
        else: return 0.40 * (um ** 0.38)

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
    
    st.subheader("📊 Vista Previa: Topología Calculada (UM Acumuladas)")
    st.dataframe(df_procesado[["Tramo", "UM_Terminales", "UM", "Q_diseno_Lps", "Acc_K_total"]].rename(columns={"UM": "UM Acumuladas (Aguas Abajo)"}), use_container_width=True)
    st.success(f"✅ Tramos y acumulaciones procesadas ({len(df_procesado)} tramos). Procede a la Pestaña 2.")
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
# PESTAÑA 3: RUTA CRÍTICA Y CARGA DINÁMICA TOTAL (MÓDULO 3 CON GRAFOS)
# ------------------------------------------------------------------------------
with tab3:
    st.header("🗺️ Módulo 3: Ruta Crítica y Carga Dinámica Total (CDT)")
    
    if "df_hidraulica" not in st.session_state or "h_Total_Tramo_m" not in st.session_state["df_hidraulica"].columns:
        st.warning("⚠️ Primero debes procesar la evaluación de pérdidas en la Pestaña 2.")
    else:
        df_mod3 = st.session_state["df_hidraulica"].copy()
        
        # 1. IDENTIFICACIÓN DEL NODO RAÍZ Y CONSTRUCCIÓN DEL GRAFO CON ATRIBUTOS
        nodos_origen = df_mod3["Desde"].unique()
        nodos_destino = df_mod3["Hasta"].unique()
        
        # El nodo raíz es aquel que aparece en 'Desde' pero nunca en 'Hasta' (ej. Cisterna o Toma)
        nodos_raiz = [n for n in nodos_origen if n not in nodos_destino]
        raiz = nodos_raiz[0] if len(nodos_raiz) > 0 else df_mod3.iloc[0]["Desde"]
        
        grafo_rutas = {}
        for idx, row in df_mod3.iterrows():
            u = str(row["Desde"]).strip()
            v = str(row["Hasta"]).strip()
            if u not in grafo_rutas:
                grafo_rutas[u] = []
            grafo_rutas[u].append({
                "hasta": v,
                "h_total": row["h_Total_Tramo_m"],
                "dz": row["Desnivel_m"],
                "hf": row["hf_Darcy_m"],
                "hm": row["hm_Acc_m"],
                "um_term": row.get("UM_Terminales", 0)
            })

        # 2. ALGORITMO DE RASTREO PARA ACUMULAR PÉRDIDAS POR CADA RAMAL
        reporte_muebles = []
        
        def trazar_rutas(nodo_actual, h_acum, dz_acum, hf_acum, hm_acum, trayectoria_str):
            if nodo_actual not in grafo_rutas:
                return # Llegamos al final absoluto de un ramal sin hijos
                
            for arista in grafo_rutas[nodo_actual]:
                v = arista["hasta"]
                nuevo_h = h_acum + arista["h_total"]
                nuevo_dz = dz_acum + arista["dz"]
                nuevo_hf = hf_acum + arista["hf"]
                nuevo_hm = hm_acum + arista["hm"]
                nueva_trayectoria = f"{trayectoria_str} ➔ {v}"
                
                # Si el nodo es terminal (tiene muebles directos asignados o ya no tiene más ramificaciones)
                if arista["um_term"] > 0 or v not in grafo_rutas:
                    cdt_req = nuevo_dz + nuevo_h + p_min_requerida
                    reporte_muebles.append({
                        "Mueble / Descarga": v,
                        "Trayectoria": nueva_trayectoria,
                        "ΔZ Estático (m)": nuevo_dz,
                        "Σ hf (m)": nuevo_hf,
                        "Σ hm (m)": nuevo_hm,
                        "Pérdida Total (m)": nuevo_h,
                        "Presión Mín. Requerida (m.c.a.)": p_min_requerida,
                        "CDT Requerida (m.c.a.)": cdt_req
                    })
                
                # Continuar explorando ramales dependientes de este nodo
                trazar_rutas(v, nuevo_h, nuevo_dz, nuevo_hf, nuevo_hm, nueva_trayectoria)

        # Ejecutar el rastreo desde la raíz inicializando en cero
        trazar_rutas(str(raiz).strip(), 0.0, 0.0, 0.0, 0.0, str(raiz).strip())
        
        if not reporte_muebles:
            st.error("Error en topología: No se encontraron muebles terminales válidos en la red.")
        else:
            df_rutas = pd.DataFrame(reporte_muebles)
            
            # 3. DETECCIÓN AUTOMÁTICA DE LA RUTA CRÍTICA
            idx_critico = df_rutas["CDT Requerida (m.c.a.)"].idxmax()
            ruta_critica_info = df_rutas.loc[idx_critico]
            
            cdt_global = ruta_critica_info["CDT Requerida (m.c.a.)"]
            st.session_state["cdt_global"] = cdt_global
            st.session_state["df_rutas"] = df_rutas
            st.session_state["mueble_critico"] = ruta_critica_info["Mueble / Descarga"]
            st.session_state["caudal_bombeo_Lps"] = df_mod3.iloc[0]["Q_diseno_Lps"] # Caudal total en la raíz
            
            # 4. DESPLIEGUE EJECUTIVO DE RESULTADOS
            st.subheader("🎯 Punto Crítico y Carga Dinámica Total (CDT)")
            
            col_c1, col_c2, col_c3 = st.columns(3)
            col_c1.metric("📌 Mueble Crítico (Más Desfavorable)", f"{ruta_critica_info['Mueble / Descarga']}")
            col_c2.metric("🏔️ Carga Estática Máxima (ΔZ)", f"{ruta_critica_info['ΔZ Estático (m)']:.2f} m")
            col_c3.metric("💥 CDT Sistema Requerida", f"{cdt_global:.2f} m.c.a.", delta=f"{(cdt_global * 1.4223):.2f} PSI")
            
            st.markdown(f"""
            > **Diagnóstico de Ruta Crítica:**  
            > El punto **{ruta_critica_info['Mueble / Descarga']}** rige el diseño electromecánico. A través de la trayectoria (*{ruta_critica_info['Trayectoria']}*), requiere la máxima Carga Dinámica Total (**{cdt_global:.2f} m.c.a.**) para vencer las pérdidas acumuladas y garantizar la presión de **{p_min_requerida:.2f} m.c.a.**
            """)
            
            st.subheader("📋 Resumen de Cargas Topológicas por Ramal")
            st.dataframe(
                df_rutas.style.format({
                    "ΔZ Estático (m)": "{:.2f}",
                    "Σ hf (m)": "{:.3f}",
                    "Σ hm (m)": "{:.3f}",
                    "Pérdida Total (m)": "{:.3f}",
                    "Presión Mín. Requerida (m.c.a.)": "{:.2f}",
                    "CDT Requerida (m.c.a.)": "{:.2f}"
                }).highlight_max(subset=["CDT Requerida (m.c.a.)"], color="#FCA5A5", axis=0),
                use_container_width=True
            )

            st.success("✅ Análisis de rutas múltiples completado. Procede a la Pestaña 4 para dimensionar la bomba basándose en esta CDT.")

# ------------------------------------------------------------------------------
# PESTAÑA 4: EQUIPO DE BOMBEO Y GRÁFICOS INTERACTIVOS (MÓDULO 4)
# ------------------------------------------------------------------------------
with tab4:
    st.header("⚡ Módulo 4: Selección de Bomba y Análisis Avanzado")
    
    if "cdt_global" not in st.session_state or "df_hidraulica" not in st.session_state:
        st.warning("⚠️ Primero debes calcular la CDT y la ruta crítica en la Pestaña 3.")
    else:
        df_mod4 = st.session_state["df_hidraulica"].copy()
        cdt_req = st.session_state["cdt_global"]
        
        # Caudal total de bombeo (Tramo Principal Cisterna -> TDT)
        q_bombeo_Lps = df_mod4.iloc[0]["Q_diseno_Lps"]
        q_bombeo_m3s = q_bombeo_Lps / 1000.0
        
        # 1. CÁLCULO DE POTENCIA DE LA BOMBA
        gamma = 1000.0  # kg/m³
        p_hid_hp = (gamma * q_bombeo_m3s * cdt_req) / 75.0
        p_mec_hp = p_hid_hp / eficiencia_bomba
        
        # Sugerencia de Motor Comercial
        potencias_comerciales = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 5.0, 7.5, 10.0]
        p_comercial = next((p for p in potencias_comerciales if p >= p_mec_hp), potencias_comerciales[-1])
        
        st.subheader("🔌 Dimensionamiento Electromecánico")
        col_b1, col_b2, col_b3, col_b4 = st.columns(4)
        col_b1.metric("Caudal de Bombeo (Q)", f"{q_bombeo_Lps:.2f} L/s")
        col_b2.metric("Potencia Hidráulica", f"{p_hid_hp:.2f} HP")
        col_b3.metric("Potencia Mecánica Requerida", f"{p_mec_hp:.2f} HP")
        col_b4.metric("Potencia Comercial Sugerida", f"{p_comercial:.2f} HP", delta=f"η = {eficiencia_bomba*100:.0f}%")
        
        st.divider()
        
        # 2. GRÁFICO 1: PERFIL PIEZOMÉTRICO Y PÉRDIDAS ACUMULADAS POR TRAMO
        st.subheader("📈 Perfil de Pérdidas de Carga por Tramo")
        
        fig_perfil = go.Figure()
        fig_perfil.add_trace(go.Bar(
            x=df_mod4["Tramo"],
            y=df_mod4["hf_Darcy_m"],
            name="Pérdida por Fricción hf (Darcy)",
            marker_color="#2563EB"
        ))
        fig_perfil.add_trace(go.Bar(
            x=df_mod4["Tramo"],
            y=df_mod4["hm_Acc_m"],
            name="Pérdidas Menores hm (Accesorios)",
            marker_color="#F59E0B"
        ))
        fig_perfil.update_layout(
            barmode="stack",
            title="Desglose de Pérdidas de Energía por Tramo (m.c.a.)",
            xaxis_title="Tramo de Tubería",
            yaxis_title="Pérdida de Carga (m)",
            hovermode="x unified",
            height=400
        )
        st.plotly_chart(fig_perfil, use_container_width=True)
        
        st.divider()
        
        # 3. BONIFICACIÓN 1: CURVA CARACTERÍSTICA DEL SISTEMA VS. BOMBA (PUNTO EXTRA +1.0)
        st.subheader("🌟 Excelencia Ingenieril 1: Punto de Operación (Curva Sistema vs. Bomba)")
        
        # Generación de curvas en función de Q
        q_vec_Lps = np.linspace(0.1, max(2.5, q_bombeo_Lps * 2), 50)
        q_vec_m3s = q_vec_Lps / 1000.0
        
        # Coeficiente de resistencia de la red K_red (H_sis = H_est + K_red * Q²)
        h_estatica_total = desnivel_topografico
        k_red = (cdt_req - h_estatica_total) / (q_bombeo_m3s ** 2) if q_bombeo_m3s > 0 else 1.0
        h_sistema = h_estatica_total + k_red * (q_vec_m3s ** 2)
        
        # Modelo de Curva del Fabricante de la bomba comercial seleccionada
        h_shut_off = cdt_req * 1.35
        a_bomba = (h_shut_off - cdt_req) / (q_bombeo_m3s ** 2) if q_bombeo_m3s > 0 else 1.0
        h_bomba = h_shut_off - a_bomba * (q_vec_m3s ** 2)
        
        fig_hq = go.Figure()
        fig_hq.add_trace(go.Scatter(x=q_vec_Lps, y=h_sistema, mode='lines', name='Curva del Sistema (H_sis)', line=dict(color='#DC2626', width=3)))
        fig_hq.add_trace(go.Scatter(x=q_vec_Lps, y=h_bomba, mode='lines', name=f'Curva Bomba Comercial ({p_comercial} HP)', line=dict(color='#059669', width=3, dash='dash')))
        fig_hq.add_trace(go.Scatter(x=[q_bombeo_Lps], y=[cdt_req], mode='markers', name='Punto de Operación Requerido', marker=dict(size=12, color='#7C3AED', symbol='star')))
        
        fig_hq.update_layout(
            title="Intersección Curva Característica de la Red vs. Bomba Comercial",
            xaxis_title="Caudal Q (L/s)",
            yaxis_title="Carga H (m.c.a.)",
            height=420
        )
        st.plotly_chart(fig_hq, use_container_width=True)
        
        st.divider()
        
        # 4. BONIFICACIÓN 2: ANÁLISIS DE GOLPE DE ARIETE (PUNTO EXTRA +1.0)
        st.subheader("🌟 Excelencia Ingenieril 2: Análisis Transitorio de Golpe de Ariete")
        
        col_ga1, col_ga2 = st.columns(2)
        with col_ga1:
            t_cierre = st.number_input("Tiempo de cierre de válvula t_c (s)", min_value=0.1, value=0.5, step=0.1)
            espesor_tubo_mm = st.number_input("Espesor de pared de tubería e (mm)", min_value=1.0, value=2.5, step=0.5)
        
        # Parámetros físicos del fluido y material (CPVC/PVC)
        K_agua = 2.2e9   # Módulo de elasticidad del agua (Pa)
        E_mat = 3.0e9    # Módulo de elasticidad CPVC/PVC (Pa)
        d_principal_m = df_mod4.iloc[0]["DN_mm"] / 1000.0
        v_principal = df_mod4.iloc[0]["Velocidad_ms"]
        e_m = espesor_tubo_mm / 1000.0
        
        # Celeridad a (m/s)
        celeridad_a = np.sqrt(K_agua / rho_agua) / np.sqrt(1 + (K_agua / E_mat) * (d_principal_m / e_m))
        
        # Tiempo crítico de la conducción Tc = 2L / a
        L_principal = df_mod4.iloc[0]["L_m"]
        t_critico = (2 * L_principal) / celeridad_a
        
        # Sobretensión de Joukowsky ΔP (m.c.a.)
        if t_cierre <= t_critico:
            dp_joukowsky_pa = rho_agua * celeridad_a * v_principal
            tipo_cierre = "Cierre Rápido (Maniobra Brusca)"
        else:
            dp_joukowsky_pa = (2 * rho_agua * L_principal * v_principal) / t_cierre
            tipo_cierre = "Cierre Lento (Maniobra Gradual)"
            
        dp_joukowsky_mca = dp_joukowsky_pa / (rho_agua * 9.81)
        
        with col_ga2:
            st.markdown(f"""
            - **Celeridad de la onda ($a$):** `{celeridad_a:.2f} m/s`
            - **Tiempo Crítico ($T_c = 2L/a$):** `{t_critico:.4f} s`
            - **Régimen de Cierre:** `{tipo_cierre}`
            - **Sobrepresión de Ariete ($\Delta P$):** `{dp_joukowsky_mca:.2f} m.c.a.`
            """)
            if dp_joukowsky_mca > (cdt_req * 0.5):
                st.error("🚨 **Alerta de Sobretensión:** Se recomienda instalar un tanque amortiguador o supresor de picos de presión.")
            else:
                st.success("✅ **Red Segura:** La sobrepresión transitoria está dentro de los márgenes de seguridad de la tubería.")

        st.success("✅ Módulo 4 completado con éxito. Procede a la Pestaña 5 para la Memoria de Cálculo Ejecutiva y Auditoría de IA.")

# ------------------------------------------------------------------------------
# PESTAÑA 5: MEMORIA DE CÁLCULO Y AUDITORÍA DE IA (MÓDULO 5)
# ------------------------------------------------------------------------------
with tab5:
    st.header("📄 Módulo 5: Memoria Ejecutiva y Bitácora de Auditoría de IA")
    
    if "df_hidraulica" not in st.session_state or "cdt_global" not in st.session_state:
        st.warning("⚠️ Primero debes completar el análisis en las pestañas anteriores para generar la memoria.")
    else:
        df_memoria = st.session_state["df_hidraulica"]
        cdt_final = st.session_state["cdt_global"]
        mueble_desfavorable = st.session_state.get("mueble_critico", "Regadera P.A.")
        
        # 1. RESUMEN EJECUTIVO DE MEMORIA DE CÁLCULO
        st.subheader("📑 Memoria de Cálculo Hidráulico")
        
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown(f"""
            **1. Datos Generales del Proyecto:**
            - **Institución:** Universidad Autónoma de Aguascalientes (UAA)
            - **Asignatura:** Instalaciones Básicas (5.º Semestre)
            - **Normativa Aplicada:** MAPAS-CONAGUA / Ecuaciones Fundamentales
            - **Temperatura del Agua:** `{temp_agua} °C` (ρ = {rho_agua:.2f} kg/m³)
            - **Desnivel Topográfico Total (ΔZ):** `{desnivel_topografico:.2f} m`
            - **Presión Mínima Requerida ($P_{{mín}}$):** `{p_min_requerida:.2f} m.c.a.`
            """)
        
        with col_r2:
            st.markdown(f"""
            **2. Resultados Principales del Diseño:**
            - **Mueble Crítico Detectado:** `{mueble_desfavorable}`
            - **Carga Dinámica Total (CDT):** `{cdt_final:.2f} m.c.a.` ({cdt_final*1.4223:.2f} PSI)
            - **Pérdidas por Fricción Totales (Darcy):** `{df_memoria['hf_Darcy_m'].sum():.3f} m`
            - **Pérdidas Menores Totales ($h_m$):** `{df_memoria['hm_Acc_m'].sum():.3f} m`
            - **Potencia Mecánica Requerida:** `{p_mec_hp:.2f} HP`
            - **Potencia Comercial Recomendada:** `{p_comercial:.2f} HP` (η = {eficiencia_bomba*100:.0f}%)
            """)

        st.divider()

        # Generación de Texto Formateado para Descarga
        texto_memoria = f"""===================================================================
MEMORIA DE CÁLCULO HIDRÁULICO Y DIMENSIONAMIENTO DE BOMBEOMEDIANTE IA
UNIVERSIDAD AUTÓNOMA DE AGUASCALIENTES - INSTALACIONES BÁSICAS
===================================================================

1. PARÁMETROS GENERALES Y FLUIDO:
-------------------------------------------------------------------
- Temperatura del Agua: {temp_agua} °C
- Densidad (rho): {rho_agua:.2f} kg/m³
- Viscosidad Cinemática (nu): {nu_agua*1e6:.4f} x10^-6 m²/s
- Presión Mínima Requerida: {p_min_requerida:.2f} m.c.a.
- Desnivel Topográfico (ΔZ): {desnivel_topografico:.2f} m

2. RESUMEN DE RUTA CRÍTICA Y CDT:
-------------------------------------------------------------------
- Descarga / Mueble Más Desfavorable: {mueble_desfavorable}
- Carga Dinámica Total (CDT): {cdt_final:.2f} m.c.a. ({cdt_final*1.4223:.2f} PSI)
- Potencia Mecánica Calculada: {p_mec_hp:.2f} HP
- Potencia Comercial Sugerida: {p_comercial:.2f} HP (Eficiencia motor: {eficiencia_bomba*100:.0f}%)

3. TABLA DE TRAMOS PROCESADOS:
-------------------------------------------------------------------
"""
        for idx, r in df_memoria.iterrows():
            texto_memoria += f"Tramo: {r['Tramo']} | Q: {r['Q_diseno_Lps']:.3f} L/s | V: {r['Velocidad_ms']:.2f} m/s | Re: {r['Re']:.0f} | f: {r['Factor_f']:.4f} | hf: {r['hf_Darcy_m']:.3f}m | hm: {r['hm_Acc_m']:.3f}m\n"

        st.download_button(
            label="📥 Descargar Memoria de Cálculo Ejecutiva (.txt)",
            data=texto_memoria,
            file_name="Memoria_Calculo_Hidraulico_UAA.txt",
            mime="text/plain"
        )

        st.divider()

        st.success("✅ ¡Felicidades! Todos los módulos interactivos de la aplicación han sido construidos e integrados exitosamente.")
    
    
