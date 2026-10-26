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
def validar_estado_fisico(tensor: np.ndarray, tipo_mat: str, sigma_y: float, phi: float) -> list:
    """Valida la coherencia física dependiendo del tipo de material."""
    errores = []
    
    # 1. Simetría obligatoria para todo tensor de Cauchy
    if not np.allclose(tensor, tensor.T, atol=1e-5):
        errores.append("Física inválida: El tensor de esfuerzos debe ser estrictamente simétrico.")
        
    # 2. Validaciones específicas por material
    if tipo_mat == "Acero (Dúctil)":
        if sigma_y <= 0:
            errores.append("Material inválido: El límite de fluencia (σ_y) debe ser mayor a 0.")
    elif tipo_mat == "Geomaterial (Suelo/Roca)":
        if not (0 <= phi < 90):
            errores.append("Geomaterial inválido: El ángulo de fricción (φ) debe estar en el intervalo [0°, 90°).")
            
    return errores

def calcular_estado_esfuerzos(tensor: np.ndarray) -> dict:
    """
    Descompone el tensor de esfuerzos en sus invariantes, 
    esfuerzos principales y su componente desviadora.
    Asume que el tensor entrante está en convención de Tensión (+).
    """
    # 1. Esfuerzos Principales y Direcciones
    e_vals, e_vecs = np.linalg.eigh(tensor)
    idx = np.argsort(e_vals)[::-1]
    
    sigma_1, sigma_2, sigma_3 = e_vals[idx]
    
    # Ordenamos también los vectores propios (columnas de e_vecs)
    e_vecs = e_vecs[:, idx]
    n_1, n_2, n_3 = e_vecs[:, 0], e_vecs[:, 1], e_vecs[:, 2]
    
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
    J2 = max(0.0, J2) 
    
    # 6. Cortante Máximo y Esfuerzo Octaédrico
    tau_max = (sigma_1 - sigma_3) / 2.0
    tau_oct = np.sqrt((2.0 * J2) / 3.0)
    
    return {
        "principales": (sigma_1, sigma_2, sigma_3),
        "direcciones": (n_1, n_2, n_3), # <-- ¡AQUÍ AGREGAMOS LAS DIRECCIONES!
        "invariantes_I": (I1, I2, I3),
        "presion_p": p,
        "desviador_s": s,
        "invariantes_J": (J2, J3),
        "cortantes": (tau_max, tau_oct)
    }

def evaluar_criterios_ductiles(sigma_1: float, sigma_3: float, J2: float, sigma_y: float) -> dict:
    """
    Evalúa los criterios de falla para materiales dúctiles (Tresca y von Mises).
    Físicamente, asume que la falla ocurre por esfuerzo cortante o energía de distorsión.
    """
    # ==========================================
    # 1. CRITERIO DE TRESCA (Esfuerzo Cortante Máximo)
    # ==========================================
    # Físicamente: La falla ocurre cuando el esfuerzo cortante máximo
    # alcanza el esfuerzo cortante de fluencia.
    q_tresca = sigma_1 - sigma_3 # Diferencia principal[cite: 8]
    
    # Validación Rúbrica: Estado hidrostático
    if np.isclose(q_tresca, 0.0, atol=1e-6):
        fs_tresca = float('inf') # FS infinito sin error de división[cite: 6]
    else:
        fs_tresca = sigma_y / q_tresca #[cite: 8]
        
    # ==========================================
    # 2. CRITERIO DE VON MISES (Energía de Distorsión Máxima)
    # ==========================================
    # Físicamente: La falla ocurre cuando la energía de distorsión
    # alcanza la del ensayo de tensión uniaxial.
    sigma_vm = np.sqrt(3.0 * J2) # Esfuerzo equivalente de von Mises[cite: 8]
    
    # Validación Rúbrica: Estado hidrostático (J2 = 0)[cite: 6]
    if np.isclose(J2, 0.0, atol=1e-6) or np.isclose(sigma_vm, 0.0, atol=1e-6):
        fs_vm = float('inf') #[cite: 6]
    else:
        fs_vm = sigma_y / sigma_vm #[cite: 8]
        
    return {
        "tresca_q": q_tresca,
        "tresca_fs": fs_tresca,
        "vm_sigma": sigma_vm,
        "vm_fs": fs_vm
    }

def evaluar_criterios_geomateriales(sigma_1_t: float, sigma_3_t: float, I1: float, J2: float, c: float, phi_deg: float) -> dict:
    """
    Evalúa criterios para suelos y rocas.
    Maneja internamente la dualidad de convenciones exigida por la rúbrica.
    """
    phi_rad = np.radians(phi_deg)
    
    # ==========================================
    # 1. CRITERIO DE MOHR-COULOMB 
    # ==========================================
    # La rúbrica exige que MC use Compresión +
    # Transformamos nuestros principales de Tensión + a Compresión +
    sigma_1_c = -sigma_3_t  # El más negativo en tensión es el más compresivo
    sigma_3_c = -sigma_1_t  # El más positivo en tensión es el menos compresivo
    
    N_phi = np.tan(np.radians(45.0 + phi_deg / 2.0))**2 #[cite: 8]
    theta = 45.0 + phi_deg / 2.0 #[cite: 8]
    
    # Esfuerzo sigma_1 requerido para fallar bajo el sigma_3 actual
    sigma_1_falla = sigma_3_c * N_phi + 2.0 * c * np.sqrt(N_phi) #[cite: 8]
    
    sigma_m = (sigma_1_c + sigma_3_c) / 2.0 #[cite: 8]
    R = (sigma_1_c - sigma_3_c) / 2.0 #[cite: 8]
    
    # Validación Rúbrica: Estado hidrostático
    if np.isclose(R, 0.0, atol=1e-6):
        fs_mc = float('inf')
    else:
        fs_mc = (c * np.cos(phi_rad) + sigma_m * np.sin(phi_rad)) / R #[cite: 8]
        
    # ==========================================
    # 2. CRITERIO DE DRUCKER-PRAGER
    # ==========================================
    # La rúbrica establece Tensión + para Drucker-Prager[cite: 8]
    # Calibración para compresión triaxial
    denominador = np.sqrt(3.0) * (3.0 - np.sin(phi_rad))
    alpha = (2.0 * np.sin(phi_rad)) / denominador #[cite: 8]
    k = (6.0 * c * np.cos(phi_rad)) / denominador #[cite: 8]
    
    F_dp = alpha * I1 + np.sqrt(J2) - k #[cite: 8]
    
    if np.isclose(J2, 0.0, atol=1e-6):
        fs_dp = float('inf') #[cite: 9]
    else:
        fs_dp = (k - alpha * I1) / np.sqrt(J2) #[cite: 9]
        
    # Validación de Tensión existente (sigma_1 en tensión positiva > 0)
    hay_tension = sigma_1_t > 1e-5
    
    return {
        "mc_Nphi": N_phi,
        "mc_s1falla": sigma_1_falla,
        "mc_theta": theta,
        "mc_fs": fs_mc,
        "dp_alpha": alpha,
        "dp_k": k,
        "dp_F": F_dp,
        "dp_fs": fs_dp,
        "hay_tension": hay_tension
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
tipo_material = st.sidebar.radio(
    "Seleccione el tipo de material:", 
    ["Acero (Dúctil)", "Geomaterial (Suelo/Roca)"]
)

# Inicializamos variables por defecto
sigma_y, c_coh, phi = 0.0, 0.0, 0.0

if tipo_material == "Acero (Dúctil)":
    sigma_y = st.sidebar.number_input("Límite de fluencia (σ_y) [Ej: MPa]", value=250.0, format="%.2f")
else:
    c_coh = st.sidebar.number_input("Cohesión (c) [Ej: kPa o MPa]", value=18.0, format="%.2f")
    phi = st.sidebar.number_input("Ángulo de fricción (φ) [Grados]", value=28.0, min_value=0.0, max_value=89.9, format="%.2f")

# ==========================================
# MOTOR DE EJECUCIÓN PRINCIPAL
# ==========================================
if st.sidebar.button("Calcular Estado y Criterios", type="primary"):
    
    # --- MÓDULO 1: VALIDACIONES ---
    lista_errores = validar_estado_fisico(tensor_input, tipo_material, sigma_y, phi)
    
    if len(lista_errores) > 0:
        st.error("🚨 **Error en las entradas detectado:**")
        for error in lista_errores:
            st.warning(error)
        st.stop()
        
    st.success("✅ Validaciones superadas.")
    
    # Conversión al Backend (Unificación a Tensión Positiva)
    if convencion == "Compresión (+)":
        tensor_backend = tensor_input * -1.0
        st.info("ℹ️ Convención: **Compresión (+)**. Tensor invertido internamente para cálculos.")
    else:
        tensor_backend = tensor_input
        st.info("ℹ️ Convención: **Tensión (+)**.")
        
    # --- MÓDULO 2: CÁLCULOS MATEMÁTICOS BÁSICOS ---
    estado = calcular_estado_esfuerzos(tensor_backend)
    
    st.header("📊 Análisis del Estado de Esfuerzos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Esfuerzos Principales")
        st.write(f"**σ₁:** `{estado['principales'][0]:.2f}`")
        st.caption(f"Dir n₁: `[{estado['direcciones'][0][0]:.3f}, {estado['direcciones'][0][1]:.3f}, {estado['direcciones'][0][2]:.3f}]`")
        
        st.write(f"**σ₂:** `{estado['principales'][1]:.2f}`")
        st.caption(f"Dir n₂: `[{estado['direcciones'][1][0]:.3f}, {estado['direcciones'][1][1]:.3f}, {estado['direcciones'][1][2]:.3f}]`")
        
        st.write(f"**σ₃:** `{estado['principales'][2]:.2f}`")
        st.caption(f"Dir n₃: `[{estado['direcciones'][2][0]:.3f}, {estado['direcciones'][2][1]:.3f}, {estado['direcciones'][2][2]:.3f}]`")
        
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

    st.divider()

    # Función auxiliar para la tabla de veredicto
    def str_veredicto(fs):
        if fs == float('inf'): return "✅ Resiste (∞)"
        return "✅ Resiste" if fs >= 1.0 else "❌ Falla"

    # ==========================================
    # EJECUCIÓN CONDICIONAL SEGÚN EL MATERIAL
    # ==========================================
    if tipo_material == "Acero (Dúctil)":
        # --- MÓDULO 3: EVALUACIÓN DE MATERIALES DÚCTILES ---
        st.header("⚙️ Criterios de Falla: Acero (Materiales Dúctiles)")
        
        res_ductil = evaluar_criterios_ductiles(
            estado['principales'][0], 
            estado['principales'][2], 
            estado['invariantes_J'][0], 
            sigma_y
        )
        
        col_t, col_v = st.columns(2)
        with col_t:
            st.subheader("Tresca (Cortante Máximo)")
            st.write(f"**Esfuerzo equivalente:** `{res_ductil['tresca_q']:.2f}` MPa")
            fs_t = res_ductil['tresca_fs']
            if fs_t == float('inf'): st.success("**FS Tresca:** `∞` (Estado Hidrostático)")
            elif fs_t >= 1.0: st.success(f"**FS Tresca:** `{fs_t:.3f}` (Resiste)")
            else: st.error(f"**FS Tresca:** `{fs_t:.3f}` (Falla)")
                
        with col_v:
            st.subheader("von Mises (Energía de Distorsión)")
            st.write(f"**Esfuerzo equivalente:** `{res_ductil['vm_sigma']:.2f}` MPa")
            fs_v = res_ductil['vm_fs']
            if fs_v == float('inf'): st.success("**FS von Mises:** `∞` (Estado Hidrostático)")
            elif fs_v >= 1.0: st.success(f"**FS von Mises:** `{fs_v:.3f}` (Resiste)")
            else: st.error(f"**FS von Mises:** `{fs_v:.3f}` (Falla)")

        st.divider()
        st.header("📋 Veredicto Final")
        st.table({
            "Criterio de Falla": ["Tresca", "von Mises"],
            "Factor de Seguridad (FS)": [
                f"{fs_t:.3f}" if fs_t != float('inf') else "∞", 
                f"{fs_v:.3f}" if fs_v != float('inf') else "∞"
            ],
            "Veredicto": [str_veredicto(fs_t), str_veredicto(fs_v)]
        })

    elif tipo_material == "Geomaterial (Suelo/Roca)":
        # --- MÓDULO 4: EVALUACIÓN DE GEOMATERIALES ---
        st.header("🪨 Criterios de Falla: Geomateriales (Suelos / Rocas)")
        
        res_geo = evaluar_criterios_geomateriales(
            estado['principales'][0], 
            estado['principales'][2], 
            estado['invariantes_I'][0], 
            estado['invariantes_J'][0], 
            c_coh, 
            phi
        )
        
        if res_geo['hay_tension']:
            st.warning("⚠️ **Advertencia:** El estado de esfuerzos presenta tracción (tensión). Los criterios de Mohr-Coulomb y Drucker-Prager están diseñados principalmente para compresión y pueden dar resultados poco realistas en la zona de tracción pura.")
        
        col_m, col_d = st.columns(2)
        with col_m:
            st.subheader("Mohr-Coulomb")
            st.write(f"**N_φ:** `{res_geo['mc_Nphi']:.3f}` | **θ:** `{res_geo['mc_theta']:.2f}°`")
            st.write(f"**σ₁ (falla):** `{res_geo['mc_s1falla']:.2f}` (Compresión +)")
            fs_m = res_geo['mc_fs']
            if fs_m == float('inf'): st.success("**FS Mohr-Coulomb:** `∞`")
            elif fs_m >= 1.0: st.success(f"**FS Mohr-Coulomb:** `{fs_m:.3f}` (Resiste)")
            else: st.error(f"**FS Mohr-Coulomb:** `{fs_m:.3f}` (Falla)")
                
        with col_d:
            st.subheader("Drucker-Prager")
            st.write(f"**α:** `{res_geo['dp_alpha']:.4f}` | **k:** `{res_geo['dp_k']:.2f}`")
            st.write(f"**Función F:** `{res_geo['dp_F']:.2f}`")
            fs_d = res_geo['dp_fs']
            if fs_d == float('inf'): st.success("**FS Drucker-Prager:** `∞`")
            elif fs_d >= 1.0: st.success(f"**FS Drucker-Prager:** `{fs_d:.3f}` (Resiste)")
            else: st.error(f"**FS Drucker-Prager:** `{fs_d:.3f}` (Falla)")

        st.divider()
        st.header("📋 Veredicto Final")
        st.table({
            "Criterio de Falla": ["Mohr-Coulomb", "Drucker-Prager"],
            "Factor de Seguridad (FS)": [
                f"{fs_m:.3f}" if fs_m != float('inf') else "∞", 
                f"{fs_d:.3f}" if fs_d != float('inf') else "∞"
            ],
            "Veredicto": [str_veredicto(fs_m), str_veredicto(fs_d)]
        })
