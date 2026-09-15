import streamlit as st
import math
import pandas as pd

st.set_page_config(page_title="Calculadora NOM-001-SEDE", page_icon="⚡", layout="wide")

if 'circuitos' not in st.session_state:
    st.session_state.circuitos = []

# --- FUNCIÓN DE TABLA DE AMPACIDAD (CORREGIDA PARA MÉXICO) ---
def obtener_calibre_awg(corriente_diseno):
    # Se eliminó el 14 AWG. El mínimo permitido por norma para estos circuitos es 12 AWG.
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
st.markdown("Dimensionamiento de circuitos derivados y alimentador principal.")
st.divider()

col1, col2 = st.columns([1, 1])

# --- PANEL IZQUIERDO: AGREGAR CIRCUITOS ---
with col1:
    st.header("1. Agregar Circuito Derivado")
    
    nombre_circuito = st.text_input("Nombre del Circuito:", "Circuito 1")
    tipo_carga = st.radio("Unidad de la Carga:", ["Watts (W)", "Volt-Amperes (VA)"], horizontal=True)
    carga = st.number_input("Valor de la Carga Eléctrica:", min_value=0.0, value=1000.0, step=100.0)
    
    if tipo_carga == "Watts (W)":
        fp = st.number_input("Factor de Potencia (FP):", min_value=0.1, max_value=1.0, value=0.95)
    else:
        fp = 1.0
        
    tipo_sistema = st.selectbox("Tipo de Alimentación:", [
        "Monofásico (127 V)", "Bifásico (220 V)", "Trifásico (220 V)", "Trifásico (440 V)"
    ])

    if st.button("➕ Calcular y Agregar Circuito", type="primary"):
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
        
        # Determinación de ITM y Polos
        capacidad_itm = calcular_capacidad_itm(corriente_diseno)
        polos_itm = obtener_polos(tipo_sistema)
        itm_completo = f"{capacidad_itm} A ({polos_itm})"
        
        calibre_awg = obtener_calibre_awg(corriente_diseno)

        nuevo_circuito = {
            "Nombre": nombre_circuito,
            "Sistema": tipo_sistema,
            "Carga": f"{carga} {'W' if tipo_carga == 'Watts (W)' else 'VA'}",
            "Id (A)": round(corriente_diseno, 2),
            "ITM Sugerido": itm_completo,
            "Calibre AWG": calibre_awg
        }
        st.session_state.circuitos.append(nuevo_circuito)
        st.success(f"¡{nombre_circuito} agregado exitosamente!")

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
        
        # Para simplificar la demostración académica, sumamos las corrientes de diseño de los derivados
        suma_corriente_diseno = sum(c["Id (A)"] for c in st.session_state.circuitos)
        
        capacidad_principal = calcular_capacidad_itm(suma_corriente_diseno)
        polos_principal = obtener_polos(sistema_principal)
        itm_principal = f"{capacidad_principal} A ({polos_principal})"
        calibre_principal = obtener_calibre_awg(suma_corriente_diseno)
        
        m1, m2 = st.columns(2)
        m1.metric("Carga Total Estimada (Id)", f"{suma_corriente_diseno:.2f} A")
        m2.metric("Interruptor Principal (ITM)", itm_principal)
        
        st.metric("Calibre Principal Sugerido", calibre_principal)
        
    else:
        st.info("Agrega circuitos en el panel izquierdo para calcular el interruptor principal.")
