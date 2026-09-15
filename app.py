import streamlit as st
import math

# Configuración de la página
st.set_page_config(page_title="Calculadora NOM-001-SEDE", page_icon="⚡")

st.title("⚡ Calculadora de Circuitos - NOM-001-SEDE")
st.markdown("Herramienta experta para dimensionamiento eléctrico.")
st.divider()

# --- FASE 1: DATOS DE ENTRADA BÁSICOS ---
st.header("1. Datos de Entrada")
col1, col2 = st.columns(2)

with col1:
    tipo_carga = st.radio("Unidad de la Carga:", ["Watts (W)", "Volt-Amperes (VA)"])
    carga = st.number_input("Valor de la Carga Eléctrica:", min_value=0.0, value=1800.0)

with col2:
    # Solo pedimos Factor de Potencia si son Watts
    if tipo_carga == "Watts (W)":
        fp = st.number_input("Factor de Potencia (FP):", min_value=0.1, max_value=1.0, value=0.95)
    else:
        fp = 1.0
        st.info("Al usar VA (Potencia Aparente), el FP se omite en el cálculo.")
    
    tipo_sistema = st.selectbox("Tipo de Alimentación:", [
        "Monofásico (127 V)", 
        "Bifásico (220 V)", 
        "Trifásico (220 V)", 
        "Trifásico (440 V)"
    ])

# Botón para calcular
if st.button("Calcular Dimensionamiento Básico", type="primary"):
    
    # Lógica de cálculo
    if tipo_sistema == "Monofásico (127 V)":
        fases, voltaje = "Monofásico", 127
        corriente_nominal = carga / (voltaje * fp)
    elif tipo_sistema == "Bifásico (220 V)":
        fases, voltaje = "Bifásico", 220
        corriente_nominal = carga / (voltaje * fp)
    elif tipo_sistema == "Trifásico (220 V)":
        fases, voltaje = "Trifásico", 220
        corriente_nominal = carga / (math.sqrt(3) * voltaje * fp)
    else:
        fases, voltaje = "Trifásico", 440
        corriente_nominal = carga / (math.sqrt(3) * voltaje * fp)

    corriente_diseno = corriente_nominal * 1.25
    
    capacidades_itm = [15, 20, 30, 40, 50, 60, 70, 100, 125, 150, 175, 200]
    itm_seleccionado = next((itm for itm in capacidades_itm if itm >= corriente_diseno), None)

    # --- REPORTE VISUAL (INTERFAZ WEB) ---
    st.divider()
    st.header("📊 Reporte de Dimensionamiento")
    
    # Métricas destacadas
    m1, m2, m3 = st.columns(3)
    m1.metric("Corriente Nominal (In)", f"{corriente_nominal:.2f} A")
    m2.metric("Corriente de Diseño (Id)", f"{corriente_diseno:.2f} A")
    m3.metric("Protección Sugerida (ITM)", f"{itm_seleccionado} A")
    
    st.success(f"✅ Cumple con condición Id ≤ ITM ({corriente_diseno:.2f} A ≤ {itm_seleccionado} A)")

# --- FASE 2: PUNTOS EXTRA (Opcional) ---
st.divider()
ver_avanzado = st.checkbox("Mostrar cálculo avanzado (Factores de corrección y Caída de Tensión)")

if ver_avanzado:
    st.header("2. Dimensionamiento Avanzado")
    c1, c2 = st.columns(2)
    
    with c1:
        temp = st.number_input("Temperatura ambiental (°C):", value=35.0)
        num_cond = st.number_input("Conductores en canalización:", min_value=1, value=3)
    with c2:
        longitud = st.number_input("Distancia del circuito (m):", value=15.0)
        impedancia = st.number_input("Impedancia (Z en ohms/m):", value=0.0053, format="%.4f")
    
    if st.button("Ejecutar Validación Normativa"):
        # Asumimos que el usuario ya calculó la In arriba, volvemos a calcularla rápido para evitar errores de estado
        voltaje_calc = int(tipo_sistema.split("(")[1].split(" ")[0])
        fp_calc = fp
        if "Trifásico" in tipo_sistema:
            i_n = carga / (math.sqrt(3) * voltaje_calc * fp_calc)
        else:
            i_n = carga / (voltaje_calc * fp_calc)
            
        ft = 1.08 if temp <= 25 else 1.00 if temp <= 30 else 0.96 if temp <= 35 else 0.91 if temp <= 40 else 0.87 if temp <= 45 else 0.82
        fa = 1.00 if num_cond <= 3 else 0.80 if num_cond <= 6 else 0.70 if num_cond <= 9 else 0.50 if num_cond <= 20 else 0.45 if num_cond <= 30 else 0.40
            
        corriente_corregida = i_n * ft * fa
        
        if "Monofásico" in tipo_sistema or "Bifásico" in tipo_sistema:
            caida_tension = ((2 * longitud * i_n * impedancia) / voltaje_calc) * 100
        else:
            caida_tension = ((3 * longitud * i_n * impedancia) / voltaje_calc) * 100
            
        st.subheader("Resultados Avanzados")
        m4, m5 = st.columns(2)
        m4.metric("Corriente Corregida (Ic)", f"{corriente_corregida:.2f} A")
        m5.metric("Caída de Tensión (%e)", f"{caida_tension:.2f}%")
        
        if caida_tension <= 3.0:
            st.success("ESTADO: APROBADO (Cumple límite del 3% en circuitos derivados).")
        else:
            st.error("ESTADO: RECHAZADO (Excede el 3%). ALERTA: Incrementar calibre del conductor.")
