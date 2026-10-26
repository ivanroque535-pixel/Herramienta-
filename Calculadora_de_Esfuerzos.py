import numpy as np
import streamlit as st

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Mecánica del Medio Continuo | Criterios de Falla",
    layout="wide",
)

st.title("🏗️ Calculadora de Esfuerzos y Criterios de Falla")
st.markdown("Evaluación de materiales dúctiles y geomateriales mediante tensores 3x3.")

# ==========================================
# FUNCIONES DE VALIDACIÓN Y FÍSICA (MÓDULOS 1 Y 2)
# ==========================================
def validar_estado_fisico(tensor: np.ndarray, sigma_y: float, phi: float) -> list:
    """
    Evalúa la coherencia física y matemática de las entradas antes de calcular.
    Retorna una lista de errores. Si la lista está vacía, el sistema es válido.
    """
    errores = []
    if not np.allclose(tensor, tensor.T, atol=1e-5):
        errores.append("Física inválida: El tensor de esfuerzos debe ser estrictamente simétrico (τ_ij = τ_ji).")
    if sigma_y <= 0:
        errores.append("Material inválido: El límite de fluencia (σ_y) debe ser mayor a 0.")
    if not (0 <= phi < 90):
        errores.append("Geomaterial inválido: El ángulo de fricción (φ) debe estar en el intervalo [0°, 90°).")
    return errores

def calcular_estado_esfuerzos(tensor: np.ndarray) -> dict:
    """
    Descompone el tensor de esfuerzos en sus invariantes, 
    esfuerzos principales y su componente desviadora.
    Asume que el tensor entrante está en convención de Tensión (+).
    """
    # 1. Esfuerzos Principales
    e_vals, e_vecs = np.linalg.eigh(tensor)
    idx = np.argsort(e_vals)[::-1]
    sigma_1, sigma_2, sigma_3 = e_vals[idx]
    
    # 2. Invariantes del Tensor de Esfuerzos (I1, I2, I3)
    I1 = np.trace(tensor)
    tr_T2 = np.trace(np.dot(tensor, tensor))
    I2 = 0.5 * (I1**2 - tr_T2)
    I3 = np.linalg.det(tensor)
    
    # 3. Presión Media (Estado Hidrostático)
    p = -I1 / 3.0
    
    # 4. Tensor Desviador (s)
    identidad = np.eye(3)
    s = tensor - (I1 / 3.0) * identidad
    
    # 5. Invariantes Desviadores (J2, J3)
    J2 = 0.5 * np.sum(s * s)
    J3 = np.linalg.det(s)
    J2 = max(0.0, J2) # Evita J2 negativos microscópicos por error de flotante
    
    # 6. Cortante Máximo y Esfuerzo Octaédrico
    tau_max = (sigma_1 - sigma_3) / 2.0
    tau_oct = np.sqrt((2.0 * J2) / 3.0)
    
    return {
        "principales": (sigma_1, sigma_2, sigma_3),
        "invariantes_I": (I1, I2, I3),
        "presion_p": p,
        "desviador_s": s,
        "invariantes_J": (J2, J3),
        "cortantes": (tau_max, tau_oct)
    }

# ==========================================
# INTERFAZ DE USUARIO: BARRA LATERAL (INPUTS)
# ==========================================
st.sidebar.header("1. Convención de Signos")
convencion = st.sidebar.radio(
    "Seleccione la convención positiva:", 
    ["Tensión (+)", "Compresión (+)"]
)

st.sidebar.header("2. Tensor de Esfuerzos")
st.sidebar.caption("Ingrese las componentes (matriz simétrica):")
c1, c2, c3 = st.sidebar.columns(3)

s_xx = c1.number_input("σ_xx", value=160.0, format="%.2f")
t_xy = c2.number_input("τ_xy", value=70.0, format="%.2f")
t_xz = c3.number_input("τ_xz", value=0.0, format="%.2f")

t_yx = c1.number_input("τ_yx", value=70.0, format="%.2f")
s_yy = c2.number_input("σ_yy", value=0.0, format="%.2f")
t_yz = c3.number_input("τ_yz", value=0.0, format="%.2f")

t_zx = c1.number_input("τ_zx", value=0.0, format="%.2f")
t_zy = c2.number_input("τ_zy", value=0.0, format="%.2f")
s_zz = c3.number_input("σ_zz", value=0.0, format="%.2f")

tensor_input = np.array([
    [s_xx, t_xy, t_xz],
    [t_yx, s_yy, t_yz],
    [t_zx, t_zy, s_zz]
])

st.sidebar.header("3. Parámetros del Material")
sigma_y = st.sidebar.number_input("Límite de fluencia (σ_y) [Ej: MPa]", value=250.0, format="%.2f")
c_coh = st.sidebar.number_input("Cohesión (c) [Ej: kPa o MPa]", value=0.0, format="%.2f")
phi = st.sidebar.number_input("Ángulo de fricción (φ) [Grados]", value=30.0, min_value=0.0, max_value=89.9, format="%.2f")

# ==========================================
# MOTOR DE EJECUCIÓN PRINCIPAL
# ==========================================
if st.sidebar.button("Calcular Estado y Criterios", type="primary"):
    
    # --- MÓDULO 1: VALIDACIONES ---
    lista_errores = validar_estado_fisico(tensor_input, sigma_y, phi)
    
    if len(lista_errores) > 0:
        st.error("🚨 **Error en las entradas detectado:**")
        for error in lista_errores:
            st.warning(error)
        st.stop()
        
    st.success("✅ Validaciones superadas: Tensor simétrico y parámetros lógicos.")
    
    if convencion == "Compresión (+)":
        tensor_backend = tensor_input * -1.0
        st.info("ℹ️ Convención elegida: **Compresión (+)**. Tensor invertido internamente para cálculos.")
    else:
        tensor_backend = tensor_input
        st.info("ℹ️ Convención elegida: **Tensión (+)**.")
        
    st.write("### Tensor Operativo (Backend: Tensión +)")
    st.write(tensor_backend)
    
    # --- MÓDULO 2: CÁLCULOS MATEMÁTICOS ---
    estado = calcular_estado_esfuerzos(tensor_backend)
    
    st.header("📊 Análisis del Estado de Esfuerzos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Esfuerzos Principales")
        st.write(f"**σ₁:** `{estado['principales'][0]:.2f}`")
        st.write(f"**σ₂:** `{estado['principales'][1]:.2f}`")
        st.write(f"**σ₃:** `{estado['principales'][2]:.2f}`")
        
    with col2:
        st.subheader("Invariantes (Globales)")
        st.write(f"**I₁:** `{estado['invariantes_I'][0]:.2f}`")
        st.write(f"**I₂:** `{estado['invariantes_I'][1]:.2f}`")
        st.write(f"**I₃:** `{estado['invariantes_I'][2]:.2f}`")
        
    with col3:
        st.subheader("Invariantes (Desviadores)")
        st.write(f"**J₂:** `{estado['invariantes_J'][0]:.2f}`")
        st.write(f"**J₃:** `{estado['invariantes_J'][1]:.2f}`")
        st.write(f"**Presión (p):** `{estado['presion_p']:.2f}` (Compresión +)")

    st.subheader("Esfuerzos Cortantes")
    st.write(f"**Cortante Máximo (τ_max):** `{estado['cortantes'][0]:.2f}`")
    st.write(f"**Cortante Octaédrico (τ_oct):** `{estado['cortantes'][1]:.2f}`")

    st.divider()
