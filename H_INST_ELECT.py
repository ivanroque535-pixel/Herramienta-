import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Calculadora NOM-001-SEDE", page_icon="⚡", layout="wide")

if 'circuitos' not in st.session_state:
    st.session_state.circuitos = []

# --- BASE DE DATOS NORMATIVA: NOM-001-SEDE ---
datos_nom_001 = {
    "12 AWG": {"ampacidad": 25,  "XL_PVC": 0.177, "RAC_PVC": 6.6,   "XL_ACERO": 0.223, "RAC_ACERO": 6.6},
    "10 AWG": {"ampacidad": 35,  "XL_PVC": 0.164, "RAC_PVC": 3.9,   "XL_ACERO": 0.207, "RAC_ACERO": 3.9},
    "8 AWG":  {"ampacidad": 50,  "XL_PVC": 0.171, "RAC_PVC": 2.56,  "XL_ACERO": 0.213, "RAC_ACERO": 2.56},
    "6 AWG":  {"ampacidad": 65,  "XL_PVC": 0.167, "RAC_PVC": 1.61,  "XL_ACERO": 0.210, "RAC_ACERO": 1.64},
    "4 AWG":  {"ampacidad": 85,  "XL_PVC": 0.157, "RAC_PVC": 1.02,  "XL_ACERO": 0.197, "RAC_ACERO": 1.05},
    "2 AWG":  {"ampacidad": 115, "XL_PVC": 0.148, "RAC_PVC": 0.62,  "XL_ACERO": 0.187, "RAC_ACERO": 0.66},
    "1 AWG":  {"ampacidad": 130, "XL_PVC": 0.151, "RAC_PVC": 0.52,  "XL_ACERO": 0.187, "RAC_ACERO": 0.52},
    "1/0 AWG": {"ampacidad": 150, "XL_PVC": 0.144, "RAC_PVC": 0.43,  "XL_ACERO": 0.180, "RAC_ACERO": 0.39},
    "2/0 AWG": {"ampacidad": 175, "XL_PVC": 0.141, "RAC_PVC": 0.33,  "XL_ACERO": 0.177, "RAC_ACERO": 0.33},
    "3/0 AWG": {"ampacidad": 200, "XL_PVC": 0.138, "RAC_PVC": 0.253, "XL_ACERO": 0.174, "RAC_ACERO": 0.259},
    "4/0 AWG": {"ampacidad": 230, "XL_PVC": 0.135, "RAC_PVC": 0.203, "XL_ACERO": 0.167, "RAC_ACERO": 0.207}
}

# Lista ordenada para permitir el bucle de redimensionamiento
orden_calibres = list(datos_nom_001.keys())

def obtener_calibre_base(corriente_diseno):
    for calibre, propiedades in datos_nom_001.items():
        if propiedades["ampacidad"] >= corriente_diseno:
            return calibre
    return "Requiere > 4/0 AWG"

def calcular_capacidad_itm(corriente_diseno):
    capacidades_itm = [15, 20, 30, 40, 50, 60, 70, 100, 125, 150, 175, 200, 250]
    return next((itm for itm in capacidades_itm if itm >= corriente_diseno), "Mayor a 250")

def obtener_polos(tipo_sistema):
    if "Monofásico" in tipo_sistema: return "1 polo"
    elif "Bifásico" in tipo_sistema: return "2 polos"
    else: return "3 polos"

st.title("⚡ Calculadora de Circuitos y Tableros - NOM-001-SEDE")
st.markdown("Dimensionamiento completo con Módulo Automático de Caída de Tensión (v2.0).")
st.divider()

col1, col2 = st.columns([1, 1.5]) 

# --- PANEL IZQUIERDO: AGREGAR CIRCUITOS ---
with col1:
    st.header("1. Agregar Circuito")
    
    nombre_circuito = st.text_input("Nombre del Circuito:", "Circuito 1")
    tipo_carga = st.radio("Unidad de la Carga:", ["Watts (W)", "Volt-Amperes (VA)"], horizontal=True)
    carga = st.number_input("Valor de la Carga Nominal:", min_value=0.0, value=1000.0, step=100.0)
    
    if tipo_carga == "Watts (W)":
        fp = st.number_input("Factor de Potencia (FP):", min_value=0.1, max_value=1.0, value=0.95)
    else:
        fp = 1.0
        
    tipo_sistema = st.selectbox("Tipo de Alimentación:", [
        "Monofásico (127 V)", "Bifásico (220 V)", "Trifásico (220 V)", "Trifásico (440 V)"
    ])

    # --- MÓDULO 2: OPCIONES AVANZADAS DE CAÍDA DE TENSIÓN ---
    with st.expander("🌟 Optimización de Conductores (Caída de Tensión)"):
        calc_extra = st.checkbox("Activar Módulo de Caída de Tensión Automático")
        if calc_extra:
            tipo_tramo = st.selectbox("Clasificación del Tramo:", ["Circuito Derivado (Límite 3%)", "Alimentador (Límite 2%)"])
            limite_e = 3.0 if "Derivado" in tipo_tramo else 2.0
            
            canalizacion = st.selectbox("Tipo de Canalización:", ["PVC / Aluminio (No Magnético)", "Acero (Magnético)"])
            longitud = st.number_input("Distancia de la trayectoria L (m):", min_value=1.0, value=15.0)
            temp = st.number_input("Temperatura ambiental (°C):", value=35.0)
            num_cond = st.number_input("Conductores portadores en canalización:", min_value=1, value=3)

    if st.button("➕ Calcular y Agregar Circuito", type="primary"):
        # 1. CÁLCULOS BÁSICOS (Ampacidad)
        if "Monofásico" in tipo_sistema:
            voltaje = 127
            corriente_nominal = carga / (voltaje * fp)
        elif "Bifásico" in tipo_sistema:
            voltaje = 220
            corriente_nominal = carga / (voltaje * fp)
        else:
            voltaje = 220 if "220" in tipo_sistema else 440
            corriente_nominal = carga / (math.sqrt(3) * voltaje * fp)

        corriente_diseno = corriente_nominal * 1.25
        capacidad_itm = calcular_capacidad_itm(corriente_diseno)
        polos_itm = obtener_polos(tipo_sistema)
        itm_completo = f"{capacidad_itm} A ({polos_itm})"
        
        calibre_base = obtener_calibre_base(corriente_diseno)
        calibre_final = calibre_base
        diagnostico = "Dominó Ampacidad"
        str_e = "N/A"
        str_ic = "N/A"

        # 2. MÓDULO ITERATIVO DE CAÍDA DE TENSIÓN
        if calc_extra and calibre_base in orden_calibres:
            # Factores térmicos y de agrupamiento
            ft = 1.08 if temp <= 25 else 1.00 if temp <= 30 else 0.96 if temp <= 35 else 0.91 if temp <= 40 else 0.87 if temp <= 45 else 0.82
            fa = 1.00 if num_cond <= 3 else 0.80 if num_cond <= 6 else 0.70 if num_cond <= 9 else 0.50 if num_cond <= 20 else 0.45 if num_cond <= 30 else 0.40
            str_ic = f"{(corriente_nominal * ft * fa):.2f} A"

            # Trigonometría para Z efectiva
            angulo = math.acos(fp)
            seno_phi = math.sin(angulo)
            
            # Inicio del bucle
            idx_calibre = orden_calibres.index(calibre_base)
            
            while idx_calibre < len(orden_calibres):
                calibre_actual = orden_calibres[idx_calibre]
                props = datos_nom_001[calibre_actual]
                
                rac = props["RAC_ACERO"] if "Acero" in canalizacion else props["RAC_PVC"]
                xl = props["XL_ACERO"] if "Acero" in canalizacion else props["XL_PVC"]
                
                # Fórmula de Impedancia Efectiva (Tabla 9)
                z_efectiva = (rac * fp) + (xl * seno_phi)
                
                # Fórmula de Caída de Voltaje
                if "Monofásico" in tipo_sistema or "Bifásico" in tipo_sistema:
                    e_volts = (2 * longitud * corriente_nominal * z_efectiva) / 1000
                else:
                    e_volts = (math.sqrt(3) * longitud * corriente_nominal * z_efectiva) / 1000
                
                caida_tension = (e_volts / voltaje) * 100
                
                if caida_tension <= limite_e:
                    calibre_final = calibre_actual
                    break
                else:
                    idx_calibre += 1 # Sube un calibre y repite el ciclo

            if idx_calibre >= len(orden_calibres):
                calibre_final = "> 4/0 AWG"
                diagnostico = "Límite Tensión Excedido"
            elif calibre_final != calibre_base:
                diagnostico = "Dominó Caída de Tensión"
                
            str_e = f"{caida_tension:.2f}%"

        # 3. GUARDAR EN MEMORIA
        nuevo_circuito = {
            "Nombre": nombre_circuito,
            "Sistema": tipo_sistema, 
            "In (A)": round(corriente_nominal, 2),
            "Id (A)": round(corriente_diseno, 2),
            "ITM Sugerido": itm_completo,
            "Calibre Base": calibre_base,
            "Calibre Final": calibre_final,
            "Diagnóstico": diagnostico,
            "%e (Caída)": str_e
        }
        st.session_state.circuitos.append(nuevo_circuito)
        st.success(f"¡Circuito evaluado! Dominancia: {diagnostico}")

# --- PANEL DERECHO: TABLERO Y ALIMENTADOR PRINCIPAL ---
with col2:
    st.header("2. Resumen del Tablero")
    
    if len(st.session_state.circuitos) > 0:
        df_circuitos = pd.DataFrame(st.session_state.circuitos)
        st.dataframe(df_circuitos.drop(columns=['Sistema']), use_container_width=True)
        
        if st.button("🗑️ Borrar Todos los Circuitos"):
            st.session_state.circuitos = []
            st.rerun()

        st.divider()
        st.header("3. Cálculo del Alimentador Principal (Por Ampacidad)")
        # Nota: En el Módulo 3, conectaremos la sumatoria de %e_Total aquí.
        
        sistema_principal = st.selectbox("Sistema del Tablero Principal:", [
            "Monofásico (127 V)", "Bifásico (220 V)", "Trifásico (220 V)", "Trifásico (440 V)"
        ])
        
        suma_corriente_nominal = sum(c["In (A)"] for c in st.session_state.circuitos)
        suma_corriente_diseno = sum(c["Id (A)"] for c in st.session_state.circuitos)
        
        capacidad_principal = calcular_capacidad_itm(suma_corriente_diseno)
        polos_principal = obtener_polos(sistema_principal)
        itm_principal = f"{capacidad_principal} A ({polos_principal})"
        calibre_principal = obtener_calibre_base(suma_corriente_diseno)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("In Total", f"{suma_corriente_nominal:.2f} A")
        m2.metric("Id Total", f"{suma_corriente_diseno:.2f} A")
        m3.metric("Interruptor Gral.", itm_principal)
        m4.metric("Calibre Troncal Base", calibre_principal)

        requiere_trafo = any("127" in c["Sistema"] for c in st.session_state.circuitos)
        if "440" in sistema_principal and requiere_trafo:
            st.warning("⚠️ **Alerta Técnica:** Se detectaron cargas a 127 V en un sistema principal de 440 V. Es normativamente obligatorio instalar un **Transformador Reductor Tipo Seco** (440 V a 220Y/127 V).")
        
    else:
        st.info("Agrega circuitos en el panel izquierdo para calcular el interruptor principal.")
