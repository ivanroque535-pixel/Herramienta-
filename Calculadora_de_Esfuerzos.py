import numpy as np
import streamlit as st

st.set_page_config(
    page_title="Mecánica del Medio Continuo",
    layout="wide",
)

st.title("⚡ Calculadora de Esfuerzos - Medio Continuo")


def calcular_mecanica_continuo(sigma: np.ndarray, n_raw: np.ndarray):
    norma_n = np.linalg.norm(n_raw)
    if norma_n == 0:
        raise ValueError(
            "El vector normal no puede ser el vector nulo (0,0,0)."
        )
    n = n_raw / norma_n

    # Vector de tracción y esfuerzos en el plano
    t_vec = np.dot(sigma, n)
    sigma_n = np.dot(t_vec, n)
    norma_t_cuadrado = np.dot(t_vec, t_vec)
    tau_n = np.sqrt(max(0.0, norma_t_cuadrado - sigma_n**2))

    # Invariantes originales
    I1_orig = np.trace(sigma)
    I2_orig = (
        sigma[0, 0] * sigma[1, 1]
        + sigma[1, 1] * sigma[2, 2]
        + sigma[0, 0] * sigma[2, 2]
    ) - (sigma[0, 1] ** 2 + sigma[1, 2] ** 2 + sigma[0, 2] ** 2)
    I3_orig = np.linalg.det(sigma)

    # Esfuerzos y direcciones principales
    e_vals, e_vecs = np.linalg.eigh(sigma)
    idx = np.argsort(e_vals)[::-1]
    e_vals = e_vals[idx]
    e_vecs = e_vecs[:, idx]

    sigma_1, sigma_2, sigma_3 = e_vals
    n_1, n_2, n_3 = e_vecs[:, 0], e_vecs[:, 1], e_vecs[:, 2]

    # Invariantes con esfuerzos principales
    I1_princ = sigma_1 + sigma_2 + sigma_3
    I2_princ = sigma_1 * sigma_2 + sigma_2 * sigma_3 + sigma_1 * sigma_3
    I3_princ = sigma_1 * sigma_2 * sigma_3

    return {
        "n_unitario": n,
        "norma_original": norma_n,
        "t_vec": t_vec,
        "sigma_n": sigma_n,
        "tau_n": tau_n,
        "esfuerzos_principales": (sigma_1, sigma_2, sigma_3),
        "direcciones_principales": (n_1, n_2, n_3),
        "invariantes_original": (I1_orig, I2_orig, I3_orig),
        "invariantes_principales": (I1_princ, I2_princ, I3_princ),
    }


# --- ENTRADAS EN LA BARRA LATERAL ---
st.sidebar.header("📥 Entrada de Datos")

st.sidebar.subheader("Tensor de Esfuerzos [σ]")
c1, c2, c3 = st.sidebar.columns(3)
s_xx = c1.number_input("σ_1,1", value=0.0, format="%.4f")
t_xy = c2.number_input("τ_1,2", value=0.0, format="%.4f")
t_xz = c3.number_input("τ_1,3", value=0.0, format="%.4f")

s_yy = c2.number_input("σ_2,2", value=0.0, format="%.4f")
t_yz = c3.number_input("τ_2,3", value=0.0, format="%.4f")

s_zz = c3.number_input("σ_3,3", value=0.0, format="%.4f")

tensor_sigma = np.array(
    [[s_xx, t_xy, t_xz], [t_xy, s_yy, t_yz], [t_xz, t_yz, s_zz]]
)

st.sidebar.subheader("Vector Unitario [n]")
nx = st.sidebar.number_input("n_x", value=0.0, format="%.4f")
ny = st.sidebar.number_input("n_y", value=0.0, format="%.4f")
nz = st.sidebar.number_input("n_z", value=0.0, format="%.4f")
vector_n = np.array([nx, ny, nz], dtype=float)

# --- CÁLCULO Y VISUALIZACIÓN ---
if st.sidebar.button("Calcular Esfuerzos", type="primary"):
    try:
        res = calcular_mecanica_continuo(tensor_sigma, vector_n)

        col_left, col_right = st.columns(2)

        with col_left:
            st.subheader("📋 Datos Procesados")
            st.write("**Tensor [σ]:**")
            st.write(tensor_sigma)
            st.write(f"**Vector Unitario n:** `{res['n_unitario']}`")

            st.subheader("🎯 Esfuerzos en el Plano")
            st.write(
                f"**Vector Tracción t:** `[{res['t_vec'][0]:.4f}, {res['t_vec'][1]:.4f}, {res['t_vec'][2]:.4f}]`"
            )
            st.metric("Esfuerzo Normal (σ_n)", f"{res['sigma_n']:.6f}")
            st.metric("Esfuerzo Cortante (τ_n)", f"{res['tau_n']:.6f}")

        with col_right:
            st.subheader("👑 Esfuerzos y Direcciones Principales")
            s1, s2, s3 = res["esfuerzos_principales"]
            n1, n2, n3 = res["direcciones_principales"]

            st.write(f"**σ₁:** `{s1:.6f}`")
            st.caption(f"Dirección n₁: `[{n1[0]:.4f}, {n1[1]:.4f}, {n1[2]:.4f}]`")

            st.write(f"**σ₂:** `{s2:.6f}`")
            st.caption(f"Dirección n₂: `[{n2[0]:.4f}, {n2[1]:.4f}, {n2[2]:.4f}]`")

            st.write(f"**σ₃:** `{s3:.6f}`")
            st.caption(f"Dirección n₃: `[{n3[0]:.4f}, {n3[1]:.4f}, {n3[2]:.4f}]`")

        st.divider()

        st.subheader("🔍 Comprobación de Invariantes")
        I1_o, I2_o, I3_o = res["invariantes_original"]
        I1_p, I2_p, I3_p = res["invariantes_principales"]

        ic1, ic2, ic3 = st.columns(3)
        ic1.metric("I₁ (Tensor)", f"{I1_o:.6f}", delta=f"Diff: {abs(I1_o-I1_p):.1e}")
        ic2.metric("I₂ (Tensor)", f"{I2_o:.6f}", delta=f"Diff: {abs(I2_o-I2_p):.1e}")
        ic3.metric("I₃ (Tensor)", f"{I3_o:.6f}", delta=f"Diff: {abs(I3_o-I3_p):.1e}")

    except ValueError as err:
        st.error(str(err))
