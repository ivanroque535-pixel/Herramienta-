import streamlit as st
import math
import pandas as pd

# Configuración de la página
st.set_page_config(page_title="Calculadora NOM-001-SEDE", page_icon="⚡", layout="wide")

# --- INICIALIZAR LA MEMORIA DE LA APP ---
if 'circuitos' not in st.session_state:
    st.session_state.circuitos = []

# --- FUNCIÓN DE TABLA DE AMPACIDAD (NOM-001-SEDE) ---
def obtener_calibre_awg(corriente_diseno):
    # Valores basados en Tabla 310-15(b)(16) a 75°C (Cobre)
    tabla_ampacidad = [
        (20, "14 AWG"), (25, "12 AWG"), (35, "10 AWG"),
        (50, "8 AWG"), (65, "6 AWG"), (85, "4 AWG"),
        (115, "2 AWG"), (130, "1 AWG"), (150, "1/0 AWG"),
        (175, "2/0 AWG"), (200, "3/0 AWG"), (230, "4/0 AWG")
    ]
    for ampacidad, awg in tabla_ampacidad:
        if ampacidad >= corriente_diseno:
            return awg
    return "Requiere kcmil (Mayor a 230A)"

def calcular_itm(corriente_diseno):
    capacidades_itm = [15, 20, 30, 40, 50, 60, 70, 100, 125, 150, 175, 200, 250]
    return next((itm for itm in capacidades_itm if itm >= corriente_diseno), "Mayor a 250A")

st.title("⚡ Calculadora de Circuitos y Tableros - NOM-001-SEDE")
st.markdown("Dimensionamiento de circuitos derivados y alimentador principal.")
st.divider()

col1, col2 = st.columns([1, 1])

# --- PANEL IZQUIERDO: AGREGAR CIRCUITOS ---
with col1:
    st.header("1. Agregar Circuito Derivado")
    
    nombre_circuito = st.text_input("Nombre del Circuito (Ej. Alumbrado PB):", "Circuito 1")
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
        # Lógica de cálculo nominal
        if tipo_sistema == "Monofásico (127 V)":
            voltaje = 127
            corriente_nominal = carga / (voltaje * fp)
        elif tipo_sistema == "Bifásico (220 V)":
            voltaje = 220
            corriente_nominal = carga / (voltaje * fp)
        elif tipo_sistema == "Trifásico (220 V)":
            voltaje = 220
            corriente_nominal = carga / (math.sqrt(3) * voltaje * fp)
        else:
            voltaje = 440
            corriente_nominal = carga / (math.sqrt(3) * voltaje * fp)

        corriente_diseno = corriente_nominal * 1.25
        itm_seleccionado = calcular_itm(corriente_diseno)
        calibre_awg = obtener_calibre_awg(corriente_diseno)

        # Guardar en la memoria
        nuevo_circuito = {
            "Nombre": nombre_circuito,
            "Sistema": tipo_sistema,
            "Carga": f"{carga} {'W' if tipo_carga == 'Watts (W)' else 'VA'}",
            "In (A)": round(corriente_nominal, 2),
            "Id (A)": round(corriente_diseno, 2),
            "ITM Sugerido (A)": itm_seleccionado,
            "Calibre AWG": calibre_awg
        }
        st.session_state.circuitos.append(nuevo_circuito)
        st.success(f"¡{nombre_circuito} agregado exitosamente!")

# --- PANEL DERECHO: TABLERO Y ALIMENTADOR PRINCIPAL ---
with col2:
    st.header("2. Resumen del Tablero")
    
    if len(st.session_state.circuitos) > 0:
        # Mostrar tabla de circuitos
        df_circuitos = pd.DataFrame(st.session_state.circuitos)
        st.dataframe(df_circuitos, use_container_width=True)
        
        # Botón para limpiar
        if st.button("🗑️ Borrar Todos los Circuitos"):
            st.session_state.circuitos = []
            st.rerun()

        st.divider()
        st.header("3. Cálculo del Alimentador Principal")
        
        # Calcular sumatorias
        suma_corriente_nominal = sum(c["In (A)"] for c in st.session_state.circuitos)
        
        # Para el alimentador principal, la norma indica que el Id es la In continua multiplicada por 1.25 (simplificado)
        corriente_diseno_principal = suma_corriente_nominal * 1.25
        itm_principal = calcular_itm(corriente_diseno_principal)
        calibre_principal = obtener_calibre_awg(corriente_diseno_principal)
        
        # Mostrar resultados del principal
        st.info("Estos cálculos asumen que todas las cargas sumadas coinciden en la misma fase/voltaje y tienen factor de demanda del 100%.")
        
        m1, m2 = st.columns(2)
        m1.metric("Suma In Total", f"{suma_corriente_nominal:.2f} A")
        m2.metric("Corriente de Diseño Principal", f"{corriente_diseno_principal:.2f} A")
        
        m3, m4 = st.columns(2)
        m3.metric("Interruptor Principal (ITM)", f"{itm_principal} A")
        m4.metric("Calibre Principal Sugerido", calibre_principal)
        
    else:
        st.info("Agrega circuitos en el panel izquierdo para calcular el interruptor principal.")
