import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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

def evaluar_criterios_geomateriales(sigma_1_t: float, sigma_3_t: float, I1: float, J2: float, c: float, phi_deg: float, calibracion: str) -> dict:
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
    # 2. DRUCKER-PRAGER (Calibración Dinámica)
    # ==========================================
    if calibracion == "Compresión Triaxial":
        denominador = np.sqrt(3.0) * (3.0 - np.sin(phi_rad))
    else: # Extensión Triaxial
        denominador = np.sqrt(3.0) * (3.0 + np.sin(phi_rad))
        
    alpha = (2.0 * np.sin(phi_rad)) / denominador
    k = (6.0 * c * np.cos(phi_rad)) / denominador
    
    F_dp = alpha * I1 + np.sqrt(J2) - k 
    
    if np.isclose(J2, 0.0, atol=1e-6): 
        fs_dp = float('inf') 
    else: 
        fs_dp = (k - alpha * I1) / np.sqrt(J2) 
        
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

def plot_criterios_ductiles(s1: float, s2: float, sigma_y: float):
    """
    Genera el Hexágono de Tresca y la Elipse de von Mises en esfuerzo plano.
    Dibuja el punto del estado actual de esfuerzos.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    
    # 1. Hexágono de Tresca
    tresca_x = [sigma_y, sigma_y, 0, -sigma_y, -sigma_y, 0, sigma_y]
    tresca_y = [0, sigma_y, sigma_y, 0, -sigma_y, -sigma_y, 0]
    ax.plot(tresca_x, tresca_y, 'b-', label='Tresca', linewidth=2)
    
    # 2. Elipse de von Mises (Ecuación paramétrica)
    theta = np.linspace(0, 2 * np.pi, 100)
    r = sigma_y / np.sqrt(1 - np.sin(theta) * np.cos(theta))
    vm_x = r * np.cos(theta)
    vm_y = r * np.sin(theta)
    ax.plot(vm_x, vm_y, 'r--', label='von Mises', linewidth=2)
    
    # 3. Punto de Estado Actual
    ax.plot(s1, s2, 'ko', label='Estado (σ₁, σ₂)', markersize=8, zorder=5)
    
    # Formato del gráfico
    ax.set_aspect('equal', 'box')
    ax.set_title("Criterios de Falla en Esfuerzo Plano")
    ax.set_xlabel("Esfuerzo Principal, σ₁")
    ax.set_ylabel("Esfuerzo Principal, σ₂")
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    limite = max(sigma_y, abs(s1), abs(s2)) * 1.5
    ax.set_xlim(-limite, limite)
    ax.set_ylim(-limite, limite)
    ax.legend(loc='upper right')
    
    return fig

def plot_circulos_mohr(s1, s2, s3, c_coh=0, phi_deg=0, graficar_envolvente=False):
    """
    Genera los tres círculos de Mohr.
    Dibuja la envolvente de Mohr-Coulomb si es un geomaterial.
    """
    fig, ax = plt.subplots(figsize=(8, 4))
    
    esfuerzos = sorted([s1, s2, s3], reverse=True)
    sig1, sig2, sig3 = esfuerzos

    # Cálculos de Centros y Radios
    C1, R1 = (sig1 + sig3) / 2.0, abs(sig1 - sig3) / 2.0
    C2, R2 = (sig1 + sig2) / 2.0, abs(sig1 - sig2) / 2.0
    C3, R3 = (sig2 + sig3) / 2.0, abs(sig2 - sig3) / 2.0

    # Dibujo de Círculos
    ax.add_patch(patches.Circle((C1, 0), R1, color='blue', fill=False, linewidth=1.5, label='Círculo Principal'))
    ax.add_patch(patches.Circle((C2, 0), R2, color='green', fill=False, linewidth=1.5))
    ax.add_patch(patches.Circle((C3, 0), R3, color='orange', fill=False, linewidth=1.5))

    # Envolvente de Falla (Mohr-Coulomb)
    if graficar_envolvente:
        phi_rad = np.radians(phi_deg)
        # Extendemos un poco la línea visualmente
        sigma_vals = np.linspace(min(sig3, 0) - R1, max(sig1, 0) + R1, 100)
        tau_vals = c_coh + sigma_vals * np.tan(phi_rad)
        
        ax.plot(sigma_vals, tau_vals, color='red', linestyle='-', linewidth=2, label='Envolvente M-C')
        ax.plot(sigma_vals, -tau_vals, color='red', linestyle='-', linewidth=2)

    # Formato
    ax.set_aspect('equal', 'box')
    ax.set_title("Círculos de Mohr en 3D")
    ax.set_xlabel("Esfuerzo Normal, σ")
    ax.set_ylabel("Esfuerzo Cortante, τ")
    ax.axhline(0, color='black', linewidth=1)
    ax.axvline(0, color='black', linewidth=1)
    ax.grid(True, linestyle=':', alpha=0.6)
    
    margen = R1 * 0.3 if R1 > 0 else max(10, c_coh)
    ax.set_xlim(min(sig3, 0) - margen, max(sig1, 0) + margen)
    ax.set_ylim(-(R1 + margen), R1 + margen)
    ax.legend(loc="upper right")
    
    return fig
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

s_xx = c1.number_input("σ_xx", value=0.0, format="%.2f")
t_xy = c2.number_input("τ_xy", value=0.0, format="%.2f")
t_xz = c3.number_input("τ_xz", value=0.0, format="%.2f")

t_yx = c1.number_input("τ_yx", value=0.0, format="%.2f")
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
tipo_material = st.sidebar.radio("Seleccione el tipo de material:", ["Acero (Dúctil)", "Geomaterial (Suelo/Roca)"])


# Inicializamos variables por defecto
sigma_y, c_coh, phi = 0.0, 0.0, 0.0

if tipo_material == "Acero (Dúctil)":
    sigma_y = st.sidebar.number_input("Límite de fluencia (σ_y) [Ej: MPa]", value=0.0, format="%.2f")
else:
    c_coh = st.sidebar.number_input("Cohesión (c) [Ej: kPa o MPa]", value=0.0, format="%.2f")
    phi = st.sidebar.number_input("Ángulo de fricción (φ) [Grados]", value=0.0, min_value=0.0, max_value=89.9, format="%.2f")

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

    st.write("### Tensor Operativo (Backend: Tensión +)")
    st.write(tensor_backend)
        
    # --- MÓDULO 2: CÁLCULOS MATEMÁTICOS BÁSICOS ---
    estado = calcular_estado_esfuerzos(tensor_backend)
    
    st.header("📊 Análisis del Estado de Esfuerzos")
    
    # ---------------------------------------------------------
    # TRADUCCIÓN VISUAL A LA CONVENCIÓN DEL USUARIO[cite: 8]
    # ---------------------------------------------------------
    if convencion == "Compresión (+)":
        # En compresión +, el mayor esfuerzo compresivo (positivo) viene del σ3 del backend (tensión)
        disp_s1 = -estado['principales'][2]
        disp_s2 = -estado['principales'][1]
        disp_s3 = -estado['principales'][0]
        
        disp_n1 = estado['direcciones'][2]
        disp_n2 = estado['direcciones'][1]
        disp_n3 = estado['direcciones'][0]
        
        disp_I1 = -estado['invariantes_I'][0]
        disp_I2 = estado['invariantes_I'][1]  # I2 no cambia de signo al invertir el tensor
        disp_I3 = -estado['invariantes_I'][2]
    else:
        disp_s1, disp_s2, disp_s3 = estado['principales']
        disp_n1, disp_n2, disp_n3 = estado['direcciones']
        disp_I1, disp_I2, disp_I3 = estado['invariantes_I']
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("Esfuerzos Principales")
        
        # Función auxiliar para obtener el ángulo agudo respecto al eje X
        def angulo_x(nx):
            ang = np.degrees(np.arccos(np.clip(abs(nx), -1.0, 1.0)))
            return ang

        st.write(f"**σ₁:** `{disp_s1:.2f}`")
        st.caption(f"Dir n₁: `[{disp_n1[0]:.3f}, {disp_n1[1]:.3f}, {disp_n1[2]:.3f}]`")
        st.caption(f"Ángulo con eje X (θx): `{angulo_x(disp_n1[0]):.2f}°`")
        
        st.write(f"**σ₂:** `{disp_s2:.2f}`")
        st.caption(f"Dir n₂: `[{disp_n2[0]:.3f}, {disp_n2[1]:.3f}, {disp_n2[2]:.3f}]`")
        st.caption(f"Ángulo con eje X (θx): `{angulo_x(disp_n2[0]):.2f}°`")
        
        st.write(f"**σ₃:** `{disp_s3:.2f}`")
        st.caption(f"Dir n₃: `[{disp_n3[0]:.3f}, {disp_n3[1]:.3f}, {disp_n3[2]:.3f}]`")
        st.caption(f"Ángulo con eje X (θx): `{angulo_x(disp_n3[0]):.2f}°`")
        
    with col2:
        st.subheader("Invariantes (Globales)")
        st.write(f"**I₁:** `{disp_I1:.2f}`")
        
        # Filtramos I2 e I3 para que solo salgan en Acero, tal como en la rúbrica
        if tipo_material == "Acero (Dúctil)":
            st.write(f"**I₂:** `{disp_I2:.2f}`")
            st.write(f"**I₃:** `{disp_I3:.2f}`")
            
    with col3:
        st.subheader("Invariantes (Desviadores)")
        st.write(f"**J₂:** `{estado['invariantes_J'][0]:.2f}`")
        
        # J3 siempre se calcula, pero lo mostramos junto con p según el material
        if tipo_material == "Geomaterial (Suelo/Roca)":
            st.write(f"**Presión (p):** `{estado['presion_p']:.2f}` (Compresión +)")
        else:
            st.write(f"**J₃:** `{estado['invariantes_J'][1]:.2f}`")
        
    # ------------------------------------
    # Mostrar cortantes SOLO para materiales dúctiles
    if tipo_material == "Acero (Dúctil)":
        st.subheader("Esfuerzos Cortantes")
        st.write(f"**Cortante Máximo (τ_max):** `{estado['cortantes'][0]:.2f}`")
        st.write(f"**Cortante Octaédrico (τ_oct):** `{estado['cortantes'][1]:.2f}`")
    # ------------------------------------

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
        st.header("📈 Representación Gráfica")
        fig_ductil = plot_criterios_ductiles(disp_s1, disp_s2, sigma_y)
        st.pyplot(fig_ductil)

    elif tipo_material == "Geomaterial (Suelo/Roca)":
        # --- MÓDULO 4: EVALUACIÓN DE GEOMATERIALES ---
        st.header("🪨 Criterios de Falla: Geomateriales (Suelos / Rocas)")
        
        res_geo = evaluar_criterios_geomateriales(
            estado['principales'][0], 
            estado['principales'][2], 
            estado['invariantes_I'][0], 
            estado['invariantes_J'][0], 
            c_coh, 
            phi,
            calibracion_dp # <-- NUEVO PARÁMETRO
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
        st.header("📈 Representación Gráfica")
        fig_mohr = plot_circulos_mohr(disp_s1, disp_s2, disp_s3, c_coh, phi, graficar_envolvente=True)
        st.pyplot(fig_mohr)
        
        # ==========================================
    # EXTRAS: EXPORTAR A CSV
    # ==========================================
    st.divider()
    st.subheader("💾 Exportar Reporte")
    
    # Preparamos el texto del CSV
    csv_text = "Criterio,Factor_Seguridad,Veredicto\n"
    
    if tipo_material == "Acero (Dúctil)":
        csv_text += f"Tresca,{fs_t if fs_t != float('inf') else 'Infinito'},{str_veredicto(fs_t)}\n"
        csv_text += f"von Mises,{fs_v if fs_v != float('inf') else 'Infinito'},{str_veredicto(fs_v)}\n"
    else:
        csv_text += f"Mohr-Coulomb,{fs_m if fs_m != float('inf') else 'Infinito'},{str_veredicto(fs_m)}\n"
        csv_text += f"Drucker-Prager ({calibracion_dp}),{fs_d if fs_d != float('inf') else 'Infinito'},{str_veredicto(fs_d)}\n"
        
    # Botón de descarga nativo de Streamlit
    st.download_button(
        label="📥 Descargar Veredicto (CSV)",
        data=csv_text.encode('utf-8'),
        file_name="reporte_criterios_falla.csv",
        mime="text/csv",
        type="primary"
    )


