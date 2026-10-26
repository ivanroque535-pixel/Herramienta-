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
# FUNCIONES DE VALIDACIÓN Y FÍSICA
# ==========================================
def validar_estado_fisico(tensor: np.ndarray, sigma_y: float, phi: float) -> list:
    """
    Evalúa la coherencia física y matemática de las entradas antes de calcular.
    Retorna una lista de errores. Si la lista está vacía, el sistema es válido.
    """
    errores = []
    
    # 1. Conservación del Momento Angular (Simetría del Tensor de Cauchy)
    # Comparamos la matriz con su transpuesta. np.allclose maneja errores de punto flotante.
    if not np.allclose(tensor, tensor.T, atol=1e-5):
        errores.append("Física inválida: El tensor de esfuerzos debe ser estrictamente simétrico (τ_ij = τ_ji).")
        
    # 2. Límite de fluencia positivo
    # El esfuerzo de fluencia es una magnitud escalar de capacidad resistente, no puede ser nula ni negativa.
    if sigma_y <= 0:
        errores.append("Material inválido: El límite de fluencia (σ_y) debe ser mayor a 0.")
        
    # 3. Restricciones del ángulo de fricción interna (Mohr-Coulomb / Drucker-Prager)
    # Físicamente, un material no puede tener un ángulo de fricción negativo, ni llegar a 90°.
    if not (0 <= phi < 90):
        errores.append("Geomaterial inválido: El ángulo de fricción (φ) debe estar en el intervalo [0°, 90°).")
        
    return errores

# ==========================================
# INTERFAZ DE USUARIO: BARRA LATERAL (INPUTS)
# ==========================================
st.sidebar.header("1. Convención de Signos")
# La rúbrica exige permitir elegir la convención, pero matemáticamente procesaremos todo
# como Tensión Positiva en el backend para estandarizar las fórmulas de invariantes.
convencion = st.sidebar.radio(
    "Seleccione la convención positiva:", 
    ["Tensión (+)", "Compresión (+)"]
)

st.sidebar.header("2. Tensor de Esfuerzos")
st.sidebar.caption("Ingrese las componentes (matriz simétrica):")
c1, c2, c3 = st.sidebar.columns(3)

# Solicitamos los datos. Note que tau_xy y tau_yx usan la misma variable para forzar 
# un poco la simetría visualmente, pero igual solicitamos la matriz completa.
s_xx = c1.number_input("σ_xx", value=160.0, format="%.2f")
t_xy = c2.number_input("τ_xy", value=70.0, format="%.2f")
t_xz = c3.number_input("τ_xz", value=0.0, format="%.2f")

t_yx = c1.number_input("τ_yx", value=70.0, format="%.2f") # Usualmente = τ_xy
s_yy = c2.number_input("σ_yy", value=0.0, format="%.2f")
t_yz = c3.number_input("τ_yz", value=0.0, format="%.2f")

t_zx = c1.number_input("τ_zx", value=0.0, format="%.2f") # Usualmente = τ_xz
t_zy = c2.number_input("τ_zy", value=0.0, format="%.2f") # Usualmente = τ_yz
s_zz = c3.number_input("σ_zz", value=0.0, format="%.2f")

# Construcción del tensor original del usuario
tensor_input = np.array([
    [s_xx, t_xy, t_xz],
    [t_yx, s_yy, t_yz],
    [t_zx, t_zy, s_zz]
])

st.sidebar.header("3. Parámetros del Material")
# Parámetro para materiales dúctiles (Acero)
sigma_y = st.sidebar.number_input("Límite de fluencia (σ_y) [Ej: MPa]", value=250.0, format="%.2f")

# Parámetros para Geomateriales (Suelos/Rocas)
c_coh = st.sidebar.number_input("Cohesión (c) [Ej: kPa o MPa]", value=0.0, format="%.2f")
phi = st.sidebar.number_input("Ángulo de fricción (φ) [Grados]", value=30.0, min_value=0.0, max_value=89.9, format="%.2f")

# ==========================================
# MOTOR DE EJECUCIÓN PRINCIPAL
# ==========================================
if st.sidebar.button("Calcular Estado y Criterios", type="primary"):
    
    # 1. Validar entradas Físicas
    lista_errores = validar_estado_fisico(tensor_input, sigma_y, phi)
    
    if len(lista_errores) > 0:
        st.error("🚨 **Error en las entradas detectado:**")
        for error in lista_errores:
            st.warning(error)
        st.stop() # Detiene la ejecución del script aquí si hay errores
        
    st.success("✅ Validaciones superadas: Tensor simétrico y parámetros de material lógicos.")
    
    # 2. Conversión al Backend (Unificación a Tensión Positiva)
    # La rúbrica establece que la app trabaja internamente con Tensión Positiva.
    # Si el usuario eligió Compresión +, multiplicamos el tensor por -1.
    if convencion == "Compresión (+)":
        tensor_backend = tensor_input * -1.0
        st.info("ℹ️ Convención elegida: **Compresión (+)**. El tensor ha sido invertido internamente para el cálculo.")
    else:
        tensor_backend = tensor_input
        st.info("ℹ️ Convención elegida: **Tensión (+)**.")
        
    # Mostrar el tensor que se usará para los cálculos
    st.write("### Tensor Operativo (Backend: Tensión +)")
    st.write(tensor_backend)
    
    # NOTA: En los siguientes módulos programaremos a partir de 'tensor_backend'.
