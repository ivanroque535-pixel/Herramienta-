import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Calculadora NOM-001-SEDE", page_icon="⚡", layout="wide")

if 'circuitos' not in st.session_state:
    st.session_state.circuitos = []

# --- FUNCIONES DE NORMATIVA ---
def obtener_calibre_awg(corriente_diseno):
    tabla_ampacidad = [
        (25, "12 AWG (Mínimo)"), (35, "10 AWG"),
        (50, "8 AWG"), (65, "6 AWG"), (85, "4 AWG"),
        (115, "2 AWG"), (130, "1 AWG"), (150, "1/0 AWG"),
        (175, "2/0 AWG"), (200, "3/0 AWG"), (230, "4/0 AWG")
    ]
    for ampacidad, awg in tabla_ampacidad:
        if ampacidad >= corriente_diseno:
            return awg
    return "Requiere kcmil (>230A)"

def calcular_capacidad_itm(corriente_diseno):
    capacidades_itm = [15, 20, 30, 40, 50, 60, 70, 100, 125, 150, 175, 200, 250]
    return next((itm for itm in capacidades_itm if itm >= corriente_diseno), "Mayor a 250")

def obtener_polos(tipo_sistema):
    if "Monofásico" in tipo_sistema:
        return "1 polo"
    elif "Bifásico" in tipo_sistema:
        return "2 polos"
    else:
        return "3 polos"

st.title("⚡ Calculadora de Circuitos y Tableros - NOM-001-SEDE")
st.markdown("Dimensionamiento completo con validación de caída de tensión.")
st.divider()

col1, col2 = st.columns([1, 1.5]) # El panel derecho es un poco más ancho para la tabla

# --- PANEL IZQUIERDO: AGREGAR CIRCUITOS ---
with col1:
    st.header("1. Agregar Circuito Derivado")
    
    nombre_circuito = st.text_input("Nombre del Circuito:", "Circuito 1")
    tipo_carga = st.radio("Unidad de la Carga:", ["Watts (W)", "Volt-Amperes (VA)"], horizontal=True)
    
    # Cambio 1: Se especifica Carga Nominal en el input
    carga = st.number_input("Valor de la Carga Nominal:", min_value=0.0, value=1000.0, step=100.0)
    
    if tipo_carga == "Watts (W)":
        fp = st.number_input("Factor de Potencia (FP):", min_value=0.1, max_value=1.0, value=0.95)
    else:
        fp = 1.0
        
    tipo_sistema = st.selectbox("Tipo de Alimentación:", [
        "Monofásico (127 V)", "Bifásico (220 V)", "Trifásico (220 V)", "Trifásico (440 V)"
    ])

    # --- PUNTOS EXTRA ---
    with st.expander("🌟 Opciones Avanzadas (Puntos Extra)"):
        calc_extra = st.checkbox("Calcular factores y caída de tensión para este circuito")
        if calc_extra:
            temp = st.number_input("Temperatura ambiental (°C):", value=35.0)
            num_cond = st.number_input("Conductores en canalización:", min_value=1, value=3)
            longitud = st.number_input("Distancia del circuito (m):", value=15.0)
            impedancia = st.number_input("Impedancia (Z en ohms/m):", value=0.0053, format="%.4f")

    if st.button("➕ Calcular y Agregar Circuito", type="primary"):
        # 1. Cálculos Básicos
        if "Monofásico" in tipo_sistema:
            voltaje = 127
            corriente_nominal = carga / (voltaje * fp)
        elif "Bifásico" in tipo_sistema:
            voltaje = 220
            corriente_nominal = carga / (voltaje * fp)
        elif "Trifásico (220" in tipo_sistema:
            voltaje = 220
            corriente_nominal = carga / (math.sqrt(3) * voltaje * fp)
        else:
            voltaje = 440
            corriente_nominal = carga / (math.sqrt(3) * voltaje * fp)

        corriente_diseno = corriente_nominal * 1.25
        capacidad_itm = calcular_capacidad_itm(corriente_diseno)
        polos_itm = obtener_polos(tipo_sistema)
        itm_completo = f"{capacidad_itm} A ({polos_itm})"
        calibre_awg = obtener_calibre_awg(corriente_diseno)

        # 2. Cálculos Avanzados (Si están activados)
        if calc_extra:
            ft = 1.08 if temp <= 25 else 1.00 if temp <= 30 else 0.96 if temp <= 35 else 0.91 if temp <= 40 else 0.87 if temp <= 45 else 0.82
            fa = 1.00 if num_cond <= 3 else 0.80 if num_cond <= 6 else 0.70 if num_cond <= 9 else 0.50 if num_cond <= 20 else 0.45 if num_cond <= 30 else 0.40
            
            corriente_corregida = corriente_nominal * ft * fa
            
            if "Monofásico" in tipo_sistema or "Bifásico" in tipo_sistema:
                caida_tension = ((2 * longitud * corriente_nominal * impedancia) / voltaje) * 100
            else:
                caida_tension = ((3 * longitud * corriente_nominal * impedancia) / voltaje) * 100
            
            estado_caida = "✅ OK" if caida_tension <= 3.0 else "❌ Excede 3%"
            str_ic = f"{corriente_corregida:.2f} A"
            str_e = f"{caida_tension:.2f}% ({estado_caida})"
        else:
            str_ic = "N/A"
            str_e = "N/A"

        # 3. Guardar en Memoria
        # Cambio 2: Se agregó "Carga Nominal" y la columna "In (A)"
        nuevo_circuito = {
            "Nombre": nombre_circuito,
            "Carga Nominal": f"{carga} {'W' if tipo_carga == 'Watts (W)' else 'VA'}",
            "In (A)": round(corriente_nominal, 2),
            "Id (A)": round(corriente_diseno, 2),
            "ITM Sugerido": itm_completo,
            "Calibre": calibre_awg,
            "Ic Corregida": str_ic,
            "%e (Caída)": str_e
        }
        st.session_state.circuitos.append(nuevo_circuito)
        st.success(f"¡Circuito agregado! Revisa el panel derecho.")

# --- PANEL DERECHO: TABLERO Y ALIMENTADOR PRINCIPAL ---
with col2:
    st.header("2. Resumen del Tablero")
    
    if len(st.session_state.circuitos) > 0:
        df_circuitos = pd.DataFrame(st.session_state.circuitos)
        st.dataframe(df_circuitos, use_container_width=True)
        
        if st.button("🗑️ Borrar Todos los Circuitos"):
            st.session_state.circuitos = []
            st.rerun()

        st.divider()
        st.header("3. Cálculo del Alimentador Principal")
        
        sistema_principal = st.selectbox("Sistema del Tablero Principal:", [
            "Monofásico (127 V)", "Bifásico (220 V)", "Trifásico (220 V)", "Trifásico (440 V)"
        ])
        
        # Cambio 3: Sumamos la In Total y la mostramos
        suma_corriente_nominal = sum(c["In (A)"] for c in st.session_state.circuitos)
        suma_corriente_diseno = sum(c["Id (A)"] for c in st.session_state.circuitos)
        
        capacidad_principal = calcular_capacidad_itm(suma_corriente_diseno)
        polos_principal = obtener_polos(sistema_principal)
        
        itm_principal = f"{capacidad_principal} A ({polos_principal})"
        calibre_principal = obtener_calibre_awg(suma_corriente_diseno)
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("In Total", f"{suma_corriente_nominal:.2f} A")
        m2.metric("Id Total", f"{suma_corriente_diseno:.2f} A")
        m3.metric("Interruptor Gral.", itm_principal)
        m4.metric("Calibre Troncal", calibre_principal)
        
    else:
        st.info("Agrega circuitos en el panel izquierdo para calcular el interruptor principal.")
