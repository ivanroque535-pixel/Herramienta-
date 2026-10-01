import numpy as np


def solicitar_matriz_3x3(nombre: str) -> np.ndarray:
    """Solicita al usuario los componentes de una matriz 3x3 simétrica."""
    print(f"\n--- Ingrese los componentes del {nombre} ---")
    s_xx = float(input("σ_xx: "))
    t_xy = float(input("τ_xy: "))
    t_xz = float(input("τ_xz: "))

    s_yy = float(input("σ_yy: "))
    t_yz = float(input("τ_yz: "))

    s_zz = float(input("σ_zz: "))

    return np.array([[s_xx, t_xy, t_xz], [t_xy, s_yy, t_yz], [t_xz, t_yz, s_zz]])


def solicitar_vector_3d(nombre: str) -> np.ndarray:
    """Solicita al usuario las componentes de un vector 3D."""
    print(f"\n--- Ingrese las componentes del {nombre} ---")
    nx = float(input("n_x: "))
    ny = float(input("n_y: "))
    nz = float(input("n_z: "))

    return np.array([nx, ny, nz], dtype=float)


def calcular_mecanica_continuo(sigma: np.ndarray, n_raw: np.ndarray):
    # 1. Normalización del vector de entrada
    norma_n = np.linalg.norm(n_raw)
    if norma_n == 0:
        raise ValueError(
            "El vector normal no puede ser el vector nulo (0,0,0)."
        )
    n = n_raw / norma_n

    # 2. Vector de tracción (t = σ · n)
    t_vec = np.dot(sigma, n)

    # 3. Esfuerzo normal (σ_n = t · n)
    sigma_n = np.dot(t_vec, n)

    # 4. Esfuerzo cortante (τ_n = sqrt(||t||² - σ_n²))
    norma_t_cuadrado = np.dot(t_vec, t_vec)
    tau_n = np.sqrt(max(0.0, norma_t_cuadrado - sigma_n**2))

    # 5. Invariantes estándar del tensor de esfuerzos
    I1_orig = np.trace(sigma)

    # Fórmula correcta del segundo invariante I2:
    I2_orig = (
        (sigma[0, 0] * sigma[1, 1] + sigma[1, 1] * sigma[2, 2] + sigma[0, 0] * sigma[2, 2])
        - (sigma[0, 1] ** 2 + sigma[1, 2] ** 2 + sigma[0, 2] ** 2)
    )

    I3_orig = np.linalg.det(sigma)

    # 6. Esfuerzos Principales y Direcciones Principales
    e_vals, e_vecs = np.linalg.eigh(sigma)

    # Ordenar de mayor a menor (σ1 >= σ2 >= σ3)
    idx = np.argsort(e_vals)[::-1]
    e_vals = e_vals[idx]
    e_vecs = e_vecs[:, idx]

    sigma_1, sigma_2, sigma_3 = e_vals
    n_1, n_2, n_3 = e_vecs[:, 0], e_vecs[:, 1], e_vecs[:, 2]

    # 7. Recálculo de Invariantes usando los Esfuerzos Principales
    I1_princ = sigma_1 + sigma_2 + sigma_3
    I2_princ = (
        sigma_1 * sigma_2 + sigma_2 * sigma_3 + sigma_1 * sigma_3
    )
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


if __name__ == "__main__":
    print("==================================================")
    print(" CALCULADORA DE MECÁNICA DEL MEDIO CONTINUO")
    print("==================================================")

    tensor_sigma = solicitar_matriz_3x3("Tensor de Esfuerzos [σ]")
    vector_n = solicitar_vector_3d("Vector Normal [n]")

    try:
        res = calcular_mecanica_continuo(tensor_sigma, vector_n)

        print("\n" + "=" * 50)
        print(" RESULTADOS ")
        print("=" * 50)

        print("\n--- ENTRADAS PROCESADAS ---")
        print("Tensor de Esfuerzos [σ]:")
        print(tensor_sigma)
        print(f"Vector Unitario n: {res['n_unitario']}")

        print("\n--- ESFUERZOS EN EL PLANO ---")
        print(f"Vector Tracción t  : {res['t_vec']}")
        print(f"Esfuerzo Normal σ_n: {res['sigma_n']:.6f}")
        print(f"Esfuerzo Cortante τ: {res['tau_n']:.6f}")

        print("\n--- ESFUERZOS Y DIRECCIONES PRINCIPALES ---")
        s1, s2, s3 = res["esfuerzos_principales"]
        n1, n2, n3 = res["direcciones_principales"]
        print(f"σ1 = {s1:.6f} | n1 = {n1}")
        print(f"σ2 = {s2:.6f} | n2 = {n2}")
        print(f"σ3 = {s3:.6f} | n3 = {n3}")

        print("\n--- COMPROBACIÓN DE INVARIANTES ---")
        I1_o, I2_o, I3_o = res["invariantes_original"]
        I1_p, I2_p, I3_p = res["invariantes_principales"]

        print(
            f"I1: Tensor = {I1_o:.6f} | Principales = {I1_p:.6f} | Diff = {abs(I1_o - I1_p):.2e}"
        )
        print(
            f"I2: Tensor = {I2_o:.6f} | Principales = {I2_p:.6f} | Diff = {abs(I2_o - I2_p):.2e}"
        )
        print(
            f"I3: Tensor = {I3_o:.6f} | Principales = {I3_p:.6f} | Diff = {abs(I3_o - I3_p):.2e}"
        )

    except ValueError as e:
        print(f"\n[Error]: {e}")
