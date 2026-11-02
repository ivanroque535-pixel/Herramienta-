import streamlit as st
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Calculadora NOM-001-SEDE (v2.0)", page_icon="⚡", layout="wide")

if 'circuitos' not in st.session_state:
    st.session_state.circuitos = []

# --- BASE DE DATOS NORMATIVA: NOM-001-SEDE (Tabla 9 y Ampacidad) ---
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

st.title("⚡ Módulo Integral de Caída de Potencial y Red Eléctrica (v2.0)")
st.markdown("Redimensionamiento dinámico y Análisis Visual (Tabla 9, NOM-001-SEDE).")
st.divider()

col1, col2 = st.columns([1, 1.3]) 

# --- PANEL IZQUIERDO: CIRCUITOS DERIVADOS ---
with col1:
    st.header("1. Tramos Derivados (Tablero a Carga)")
    
    nombre_circuito = st.text_input("Nombre del Circuito:", "Circuito 1")
    tipo_carga = st.radio("Unidad de la Carga:", ["Watts (W)", "Volt-Amperes (VA)"], horizontal=True)
    carga = st.number_input("Valor de la Carga Nominal:", min_value=0.0, value=0.0, step=100.0)
    
    if tipo_carga == "Watts (W)":
        fp = st.number_input("Factor de Potencia (FP):", min_value=0.1, max_value=1.0, value=0.95)
    else:
        fp = 1.0
        
    tipo_sistema = st.selectbox("Tipo de Alimentación (Derivado):", [
        "Monofásico (127 V)", "Bifásico (220 V)", "Trifásico (220 V)", "Trifásico (440 V)"
    ])

    with st.expander("🌟 Optimización por Caída de Tensión (Límite 3%)", expanded=True):
        canalizacion = st.selectbox("Canalización:", ["PVC / Aluminio (No Magnético)", "Acero (Magnético)"])
        longitud = st.number_input("Distancia del circuito L (m):", min_value=1.0, value=0.0)

    if st.button("➕ Calcular y Agregar Derivado", type="primary"):
        # 1. Ampacidad Base
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
        itm_completo = f"{calcular_capacidad_itm(corriente_diseno)} A ({obtener_polos(tipo_sistema)})"
        
        calibre_base = obtener_calibre_base(corriente_diseno)
        calibre_final = calibre_base
        diagnostico = "Ampacidad"

        # 2. Iteración de Tensión (Derivados)
        if calibre_base in orden_calibres:
            angulo = math.acos(fp)
            seno_phi = math.sin(angulo)
            idx = orden_calibres.index(calibre_base)
            
            while idx < len(orden_calibres):
                calibre_actual = orden_calibres[idx]
                props = datos_nom_001[calibre_actual]
                
                rac = props["RAC_ACERO"] if "Acero" in canalizacion else props["RAC_PVC"]
                xl = props["XL_ACERO"] if "Acero" in canalizacion else props["XL_PVC"]
                
                z_efectiva = (rac * fp) + (xl * seno_phi)
                
                if "Monofásico" in tipo_sistema or "Bifásico" in tipo_sistema:
                    e_volts = (2 * longitud * corriente_nominal * z_efectiva) / 1000
                else:
                    e_volts = (math.sqrt(3) * longitud * corriente_nominal * z_efectiva) / 1000
                
                caida_tension = (e_volts / voltaje) * 100
                
                if caida_tension <= 3.0: 
                    calibre_final = calibre_actual
                    break
                else:
                    idx += 1

            if idx >= len(orden_calibres):
                calibre_final = "> 4/0 AWG"
                diagnostico = "Excede Límite"
            elif calibre_final != calibre_base:
                diagnostico = "Tensión"
                
            str_e = caida_tension 

        nuevo_circuito = {
            "Nombre": nombre_circuito,
            "Sistema": tipo_sistema, 
            "In (A)": round(corriente_nominal, 2),
            "Id (A)": round(corriente_diseno, 2),
            "ITM": itm_completo,
            "Calibre": calibre_final,
            "Razón": diagnostico,
            "%e_deriv": round(str_e, 2)
        }
        st.session_state.circuitos.append(nuevo_circuito)

# --- PANEL DERECHO: ALIMENTADOR PRINCIPAL ---
with col2:
    st.header("2. Tramo Alimentador (Acometida a Tablero)")
    
    if len(st.session_state.circuitos) > 0:
        df_circuitos = pd.DataFrame(st.session_state.circuitos)
        st.dataframe(df_circuitos.drop(columns=['Sistema']), use_container_width=True)
        
        if st.button("🗑️ Borrar Todos"):
            st.session_state.circuitos = []
            st.rerun()

        st.divider()
        
        sistema_principal = st.selectbox("Sistema del Tablero Principal:", [
            "Monofásico (127 V)", "Bifásico (220 V)", "Trifásico (220 V)", "Trifásico (440 V)"
        ])
        
        c1, c2, c3 = st.columns(3)
        conduit_alim = c1.selectbox("Tubería Alimentador:", ["PVC/Aluminio", "Acero"])
        long_alim = c2.number_input("Longitud L (m):", min_value=1.0, value=20.0)
        fp_alim = c3.number_input("FP Global:", min_value=0.5, max_value=1.0, value=0.90)

        suma_in = sum(c["In (A)"] for c in st.session_state.circuitos)
        suma_id = sum(c["Id (A)"] for c in st.session_state.circuitos)
        voltaje_alim = 127 if "Monofásico" in sistema_principal else 220 if "220" in sistema_principal else 440
        
        calibre_alim_base = obtener_calibre_base(suma_id)
        calibre_alim_final = calibre_alim_base
        
        e_alim = 0.0
        if calibre_alim_base in orden_calibres:
            idx = orden_calibres.index(calibre_alim_base)
            angulo_alim = math.acos(fp_alim)
            seno_phi_alim = math.sin(angulo_alim)
            
            while idx < len(orden_calibres):
                cal_act = orden_calibres[idx]
                props = datos_nom_001[cal_act]
                
                rac = props["RAC_ACERO"] if "Acero" in conduit_alim else props["RAC_PVC"]
                xl = props["XL_ACERO"] if "Acero" in conduit_alim else props["XL_PVC"]
                
                z_ef = (rac * fp_alim) + (xl * seno_phi_alim)
                
                if "Monofásico" in sistema_principal or "Bifásico" in sistema_principal:
                    ev = (2 * long_alim * suma_in * z_ef) / 1000
                else:
                    ev = (math.sqrt(3) * long_alim * suma_in * z_ef) / 1000
                
                e_alim = (ev / voltaje_alim) * 100
                
                if e_alim <= 2.0: 
                    calibre_alim_final = cal_act
                    break
                else:
                    idx += 1

        peor_e_deriv = max(c["%e_deriv"] for c in st.session_state.circuitos)
        e_total = e_alim + peor_e_deriv
        estado_global = "✅ APROBADO (≤5%)" if e_total <= 5.0 else "❌ RECHAZADO (>5%)"

        st.subheader("3. Resultados del Sistema Integral")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("ITM General", f"{calcular_capacidad_itm(suma_id)} A ({obtener_polos(sistema_principal)})")
        m2.metric("Calibre Troncal", calibre_alim_final)
        m3.metric("%e Alimentador", f"{e_alim:.2f}%")
        m4.metric("%e TOTAL", f"{e_total:.2f}%", estado_global)

        if "440" in sistema_principal and any("127" in c["Sistema"] for c in st.session_state.circuitos):
            st.warning("⚠️ **Alerta:** Se requiere un **Transformador Reductor** (440V a 220Y/127V).")
            
# --- MÓDULO 4: VISUALIZACIÓN GRÁFICA ---
if len(st.session_state.circuitos) > 0:
    st.divider()
    st.header("4. Visualización Gráfica del Sistema")
    
    g1, g2 = st.columns(2)
    
    with g1:
        st.subheader("Auditoría de Caída de Tensión (%e)")
        # Preparamos datos para el gráfico de barras
        nombres = [c["Nombre"] for c in st.session_state.circuitos] + ["Alimentador Principal", "Sistema TOTAL"]
        caidas = [c["%e_deriv"] for c in st.session_state.circuitos] + [e_alim, e_total]
        colores = ['#1f77b4'] * len(st.session_state.circuitos) + ['#ff7f0e', '#d62728']
        
        fig_e = go.Figure(data=[go.Bar(x=nombres, y=caidas, marker_color=colores, text=[f"{val:.2f}%" for val in caidas], textposition='auto')])
        
        # Líneas de límite normativo
        fig_e.add_hline(y=3.0, line_dash="dash", line_color="red", annotation_text="Límite Derivados (3%)")
        fig_e.add_hline(y=5.0, line_dash="solid", line_color="darkred", annotation_text="Límite TOTAL (5%)")
        
        fig_e.update_layout(yaxis_title="Caída de Tensión (%)", showlegend=False, template="plotly_white")
        st.plotly_chart(fig_e, use_container_width=True)
        
    with g2:
        st.subheader("Distribución de Cargas (Amperes)")
        # Gráfico de pastel para ver el balance del tablero
        df_pie = pd.DataFrame(st.session_state.circuitos)
        fig_pie = px.pie(df_pie, values='In (A)', names='Nombre', hole=0.4, color_discrete_sequence=px.colors.sequential.Teal)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(annotations=[dict(text=f'Total:<br>{suma_in:.1f} A', x=0.5, y=0.5, font_size=20, showarrow=False)], template="plotly_white")
        st.plotly_chart(fig_pie, use_container_width=True)
